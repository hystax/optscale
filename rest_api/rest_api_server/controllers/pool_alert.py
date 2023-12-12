import logging
import uuid
import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import ThresholdTypes, ThresholdBasedTypes
from rest_api.rest_api_server.models.models import (PoolAlert, Pool, AlertContact,
                                                    Organization)
from rest_api.rest_api_server.controllers.base import (BaseController,
                                                       BaseHierarchicalController)
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper

LOG = logging.getLogger(__name__)
NOTIFICATION_INTERVAL = 43200  # 12 hours


class PoolAlertController(BaseController):
    def _get_model_type(self):
        return PoolAlert

    def process_alerts(self, organization_id):
        organization = self.session.query(Organization).filter(
            Organization.id == organization_id,
            Organization.deleted.is_(False)
        ).one_or_none()
        if not organization:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        affected_alerts = self.session.query(
            PoolAlert,
        ).join(
            Pool, and_(
                PoolAlert.pool_id == Pool.id,
                PoolAlert.based.notin_([ThresholdBasedTypes.CONSTRAINT,
                                        ThresholdBasedTypes.ENV_CHANGE]),
                Pool.deleted.is_(False),
                Pool.organization_id == organization_id,
            )
        ).filter(
            PoolAlert.deleted.is_(False)
        ).all()

        pool_limit_costs = PoolController(
            self.session, self._config, self.token
        ).get_pool_hierarchy_costs(organization.pool_id)

        def get_pools_children_ids(pool_id):
            children = {b_id for b_id in pool_limit_costs.get(pool_id)['children']}
            for child in children.copy():
                children.update(get_pools_children_ids(child))
            return children

        alert_map = {a.id: a for a in affected_alerts}
        alert_pools = {}
        for alert in affected_alerts:
            pool_ids = [alert.pool_id]
            if alert.include_children:
                pool_ids.extend(get_pools_children_ids(alert.pool_id))

            for pool_id in pool_ids:
                pool_info = pool_limit_costs.get(pool_id)
                based = pool_info.get(alert.based.value)
                if alert.threshold_type == ThresholdTypes.ABSOLUTE:
                    if based > alert.threshold:
                        if alert.id not in alert_pools:
                            alert_pools[alert.id] = []
                        alert_pools[alert.id].append(pool_info['id'])
                elif alert.threshold_type == ThresholdTypes.PERCENTAGE:
                    limit = pool_info['limit']
                    if ((limit > 0 and based * 100 / limit > alert.threshold) or
                            (limit == 0 and based > 0)):
                        if alert.id not in alert_pools:
                            alert_pools[alert.id] = []
                        alert_pools[alert.id].append(pool_info['id'])
            if not alert_pools.get(alert.id, []) and alert.last_shoot_at:
                alert.last_shoot_at = 0
        result = []
        tasks = []
        if alert_pools:
            alert_pool_ids = set()
            for pool_ids in alert_pools.values():
                alert_pool_ids.update(pool_ids)
            for alert_id, pool_ids in alert_pools.items():
                alert = alert_map.get(alert_id)
                now = int(datetime.datetime.utcnow().timestamp())
                last_shoot = alert.last_shoot_at
                if last_shoot and last_shoot + NOTIFICATION_INTERVAL > now:
                    continue
                for pool_id in pool_ids:
                    pool_info = pool_limit_costs.get(pool_id)
                    meta = {
                        'alert_id': alert.id,
                        'cost': pool_info[alert.based.value],
                        'limit': pool_info['limit'],
                    }
                    tasks.append([organization_id, pool_id, 'pool',
                                  'expenses_alert', meta,
                                  'alert.violation.expense'])
                alert.last_shoot_at = now
                self.session.add(alert)
                result.append(alert)
            self.session.commit()
            for task in tasks:
                self.publish_activities_task(*task)
        return result

    def add_contacts(self, alert_id, pool_id, contacts):
        employee_ids = set()
        slack_channel_ids = set()
        for contact in contacts:
            employee_id = contact.get('employee_id')
            if employee_id is not None:
                employee_ids.add(employee_id)
            slack_channel_id = contact.get('slack_channel_id')
            if slack_channel_id is not None:
                slack_team_id = contact['slack_team_id']
                slack_channel_ids.add((slack_channel_id, slack_team_id))
        self.validate_employee_contacts(pool_id, employee_ids)
        for employee_id in employee_ids:
            self.session.add(AlertContact(employee_id=employee_id,
                                          pool_alert_id=alert_id))
        for slack_channel_id, slack_team_id in slack_channel_ids:
            self.session.add(AlertContact(slack_channel_id=slack_channel_id,
                                          slack_team_id=slack_team_id,
                                          pool_alert_id=alert_id))

    def get_alert_task_meta(self, alert, user_info):
        pool = self.session.query(Pool).filter(
            and_(
                Pool.id == alert['pool_id'],
                Pool.deleted.is_(False)
            )
        ).one_or_none()
        pool_name = pool.name
        alert_based_value = alert['based'].value
        warn_type_map = {
            ThresholdBasedTypes.COST.value: 'expenses',
            ThresholdBasedTypes.FORECAST.value: 'forecast',
            ThresholdBasedTypes.CONSTRAINT.value: 'constraint violation',
            ThresholdBasedTypes.ENV_CHANGE.value: 'environment changes'
        }
        warn_type = warn_type_map.get(alert_based_value)
        with_subpools = ''
        if alert.get('include_children'):
            with_subpools = ' with sub-pools'
        alert['based'] = alert_based_value
        alert['threshold_type'] = alert['threshold_type'].value
        return {
            'initiator_name': user_info['display_name'],
            'initiator_email': user_info['email'],
            'alert': alert,
            'pool_name': pool_name,
            'with_subpools': with_subpools,
            'warn_type': warn_type,
            'object_name': 'alert(%s)' % alert['id']
        }

    def create(self, **kwargs):
        pool_id = kwargs.get('pool_id')
        contacts = kwargs.pop('contacts')
        alert_id = str(uuid.uuid4())
        self.add_contacts(alert_id, pool_id, contacts)
        alert = super().create(id=alert_id, **kwargs)
        user_info = self.get_user_info()
        meta = self.get_alert_task_meta(alert.to_dict(), user_info)
        self.publish_activities_task(
            alert.pool.organization_id, alert.to_dict()['id'], 'pool_alert',
            'alert_added', meta, 'alert.action.added', add_token=True)
        return alert

    def delete(self, item_id):
        alert = self.get(item_id)
        contacts = []
        alert_dict = alert.to_dict()
        if alert.contacts:
            for contact in alert.contacts:
                if contact.slack_channel_id or contact.slack_team_id:
                    contacts.append(AlertContact(
                        slack_channel_id=contact.slack_channel_id,
                        slack_team_id=contact.slack_team_id,
                        pool_alert_id=contact.pool_alert_id))
                self.session.delete(contact)
            try:
                self.session.commit()
            except IntegrityError as ex:
                LOG.warning('Failed to delete AlertContacts for alert %s',
                            item_id)
                self.session.rollback()
                raise WrongArgumentsException(Err.OE0003, [str(ex)])
        super().delete(item_id)
        user_info = self.get_user_info()
        meta = self.get_alert_task_meta(alert_dict, user_info)
        self.publish_activities_task(
            alert.pool.organization_id, alert_dict['id'], 'pool_alert',
            'alert_removed', meta, 'alert.action.removed', add_token=True)

    def edit(self, item_id, **kwargs):
        alert = self.get(item_id)
        contacts = kwargs.pop('contacts', None)
        self.check_update_restrictions(**kwargs)
        if kwargs:
            for key, value in kwargs.items():
                setattr(alert, key, value)
            self._validate(alert, is_new=False, **kwargs)
            self.session.add(alert)
        if contacts:
            for contact in alert.contacts:
                self.session.delete(contact)
            self.add_contacts(alert.id, alert.pool_id, contacts)
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return alert

    def validate_employee_contacts(self, pool_id, contacts):
        pool = self.session.query(Pool).filter(
            and_(
                Pool.id == pool_id,
                Pool.deleted.is_(False)
            )
        ).one_or_none()
        if not pool:
            raise NotFoundException(Err.OE0002, [Pool.__name__, pool_id])
        employees = EmployeeController(
            self.session, self._config, self.token
        )._list(pool.organization_id)
        invalid_employees = list(filter(
            lambda x: x not in list(map(lambda y: y.id, employees)), contacts))
        if invalid_employees:
            employees_str = ', '.join(invalid_employees)
            raise WrongArgumentsException(Err.OE0386, [employees_str])
        return list(filter(lambda x: x.id in contacts, employees))

    def list(self, organization_id):
        return self.session.query(PoolAlert).join(
            Pool, and_(
                Pool.organization_id == organization_id,
                Pool.deleted.is_(False),
                PoolAlert.pool_id == Pool.id,
            )
        ).filter(
            PoolAlert.deleted.is_(False),
        ).all()

    def get_alerts_by_based(self, pool_ids, based):
        return self.session.query(PoolAlert).filter(
            and_(
                PoolAlert.deleted.is_(False),
                PoolAlert.pool_id.in_(pool_ids),
                PoolAlert.based == based
            )).all()

    def get_pool_alerts_map(self, pool_ids,
                            based=ThresholdBasedTypes.ENV_CHANGE):
        pool_alerts_map = {}
        bhc = BaseHierarchicalController(
            self.session, self._config, self.token)
        all_pool_ids = set(pool_ids)

        for pool_id in pool_ids:
            pool_parents = bhc.get_item_hierarchy(
                'parent_id', pool_id, 'id', Pool, False)
            parents = [x.id for x in pool_parents]
            all_pool_ids.update(parents)

        alerts = self.session.query(PoolAlert).filter(and_(
            PoolAlert.pool_id.in_(all_pool_ids),
            PoolAlert.based == based,
            PoolAlert.deleted_at == 0,
        )).all()
        alerts_map = {alert.id: alert for alert in alerts}
        alert_contacts = self.session.query(AlertContact).filter(and_(
            AlertContact.pool_alert_id.in_(list(alerts_map.keys()))
        )).all()
        alert_contacts_map = {contact for contact in alert_contacts}

        for alert_id, alert in alerts_map.items():
            contacts = [x for x in alert_contacts_map
                        if x.pool_alert_id == alert_id]
            if not contacts:
                continue
            if alert.include_children:
                children = bhc.get_item_hierarchy(
                    'id', alert.pool_id, 'parent_id', Pool, True)
                pools = [x.id for x in children if x.id in pool_ids]
            else:
                pools = [alert.pool_id]
            for p in pools:
                if not pool_alerts_map.get(p):
                    pool_alerts_map[p] = []
                pool_alerts_map[p].append(alert_id)
        return pool_alerts_map


class PoolAlertAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolAlertController
