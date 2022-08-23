import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, or_, exists
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, FailedDependency)
from rest_api_server.controllers.base import (BaseController, MongoMixin,
                                              ResourceFormatMixin)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.pool import PoolController
from rest_api_server.controllers.cluster_type import ClusterTypeController
from rest_api_server.controllers.employee import EmployeeController
from rest_api_server.controllers.expense import ExpenseController
from rest_api_server.controllers.pool_alert import PoolAlertController
from rest_api_server.controllers.rule_apply import RuleApplyController
from rest_api_server.controllers.calendar_synchronization import (
    CalendarSynchronizationController)
from rest_api_server.exceptions import Err
from rest_api_server.models.models import (
    CloudAccount, Employee, Organization, Pool, ResourceConstraint, PoolPolicy,
    ShareableBooking, CalendarSynchronization)
from rest_api_server.models.enums import (CloudTypes, ThresholdBasedTypes)
from rest_api_server.utils import (
    check_string_attribute, check_int_attribute, check_dict_attribute,
    encoded_tags, retry_mongo_upsert, update_tags,
    generate_discovered_cluster_resources_stat, check_bool_attribute)
from cloud_adapter.model import RES_MODEL_MAP, ResourceTypes

LOG = logging.getLogger(__name__)
# mongodb resource type -> resource model in cloud adapter
RESOURCE_MODEL_MAP = {
    obj.value: RES_MODEL_MAP.get(obj.name) for obj in ResourceTypes.objects()
}


class CloudResourceController(BaseController, MongoMixin, ResourceFormatMixin):
    @staticmethod
    def get_split_fields():
        return {'cloud_account_id', 'cloud_resource_id', 'pool_id',
                'employee_id', 'created_at', 'deleted_at', '_id',
                'applied_rules', 'cluster_id', 'cluster_type_id',
                'organization_id', 'is_environment'}

    @staticmethod
    def get_validation_parameters(resource_type):
        required_fields = {
            'cloud_resource_id', 'resource_type', 'cloud_account_id'
        }
        immutable_params = {
            'created_at', 'deleted_at', 'id', '_id', 'resource_id',
            'pool_name', 'pool_purpose', 'owner_name', 'is_environment'
        }
        optional_params = {
            'name', 'region', 'pool_id', 'meta', 'tags',
            'first_seen', 'last_seen', 'created_by_kind', 'created_by_name',
            'k8s_namespace', 'k8s_node', 'k8s_service', 'cloud_created_at',
            'shareable', 'env_properties', 'service_name', 'active',
            # TODO: OS-4730: leave one allowed field for resource owner id
            'owner_id', 'employee_id'
        }
        model_specific_params = set()
        model = RESOURCE_MODEL_MAP.get(resource_type)
        if model:
            exclusions = required_fields | immutable_params
            model_specific_params.update([f for f in model().fields()
                                          if f not in exclusions])
        return (required_fields, immutable_params,
                optional_params, model_specific_params)

    def get_set_status_func(self, resource_type):
        cloud_type_set_status_func_map = {
            ResourceTypes.volume.value: self._set_volume_status_date_fields,
            ResourceTypes.instance.value: self._set_instance_status_date_fields,
            ResourceTypes.ip_address.value: self._set_ip_address_updated_fields
        }
        return cloud_type_set_status_func_map.get(resource_type)

    def get(self, item_id, include_deleted=False, **kwargs):
        result = self.list(include_deleted, _id=[item_id])
        if len(result) > 1:
            raise WrongArgumentsException(Err.OE0177, [])
        if len(result) == 1:
            return result[0]
        raise NotFoundException(Err.OE0002, ['Resource', item_id])

    def delete_bookings(self, item_id):
        bookings = self.session.query(ShareableBooking.id,
                                      ShareableBooking.organization_id,
                                      ShareableBooking.event_id).filter(
            and_(ShareableBooking.deleted.is_(False),
                 ShareableBooking.resource_id == item_id)).all()
        booking_ids = []
        event_ids = []
        org_id = None
        for booking in bookings:
            if org_id is not None and org_id != booking[1]:
                raise WrongArgumentsException(Err.OE0177, [])
            org_id = booking[1]
            booking_ids.append(booking[0])
            event_ids.append(booking[2])
        if booking_ids:
            self.session.query(ShareableBooking).filter(
                ShareableBooking.id.in_(booking_ids)).update(
                {ShareableBooking.deleted_at: int(datetime.utcnow().timestamp())},
                synchronize_session=False)
            try:
                self.session.commit()
            except IntegrityError as ex:
                LOG.warning('Failed to delete bookings for resource %s',
                            item_id)
                self.session.rollback()
                raise WrongArgumentsException(Err.OE0003, [str(ex)])
            calendar_sync = self.session.query(
                CalendarSynchronization).filter(
                and_(
                    CalendarSynchronization.deleted.is_(False),
                    CalendarSynchronization.organization_id == org_id
                )).scalar()
            if calendar_sync:
                calendar_sync_ctl = CalendarSynchronizationController(
                    self.session, self._config)
                for event_id in event_ids:
                    try:
                        calendar_sync_ctl.delete_calendar_event_by_id(
                            calendar_sync, event_id)
                    except FailedDependency as exc:
                        LOG.warning(
                            'Error deleting event calendar booking: %s', str(exc))

    def edit(self, item_id, **kwargs):
        now_ts = int(datetime.utcnow().timestamp())
        self.check_restrictions(is_new=False, **kwargs)
        if kwargs.get('employee_id'):
            self.check_entity_exists(kwargs['employee_id'], Employee)
        if kwargs.get('pool_id'):
            self.check_entity_exists(kwargs['pool_id'], Pool)
        resource = self.get(item_id)
        is_shareable = resource.get('shareable', False)
        old_properties = {}
        if kwargs.get('env_properties'):
            old_properties = resource.get('env_properties', {})
        if kwargs.get('shareable') is False:
            if resource.get('is_environment'):
                raise WrongArgumentsException(Err.OE0488, [item_id])
            self.delete_bookings(item_id)
        if kwargs.get('env_properties') is not None and not is_shareable:
            raise WrongArgumentsException(Err.OE0480, ['Resource', item_id])

        active_text_status_map = {
            True: 'Active',
            False: 'Not Active',
            None: 'Not Active'
        }
        if is_shareable:
            changed_properties_list = []
            meta = {}
            resource_pool = kwargs.get('pool_id') or resource['pool_id']
            task_type = None
            org_id = resource.get('organization_id')
            if not org_id:
                cloud_acc = self.session.query(CloudAccount).filter(
                    and_(CloudAccount.id == resource['cloud_account_id'],
                         CloudAccount.deleted.is_(False))).one_or_none()
                org_id = cloud_acc.organization_id
            if kwargs.get('active') is not None:
                if resource['active'] != kwargs['active']:
                    task_type = 'env_active_state_changed'
                    meta = {
                        'previous_state': active_text_status_map.get(
                            resource['active']),
                        'new_state': active_text_status_map.get(
                            kwargs['active'])}
            elif kwargs.get('env_properties') is not None:
                task_type = 'env_property_updated'
                kwargs['env_properties'] = self.update_history_properties(
                    resource, kwargs.get('env_properties'))
                properties = set(list(old_properties.keys()) + list(
                    kwargs['env_properties'].keys()))
                for prop_name in properties:
                    previous_env_prop = old_properties.get(prop_name)
                    new_env_prop = kwargs['env_properties'].get(prop_name)
                    if new_env_prop != previous_env_prop:
                        changed_properties_list.append({
                            'name': prop_name,
                            'previous_value': previous_env_prop,
                            'new_value': new_env_prop
                        })
                meta['env_properties'] = changed_properties_list

            if task_type:
                pool_alerts_map = PoolAlertController(
                    self.session, self._config, self.token
                ).get_pool_alerts_map([resource_pool],
                                      ThresholdBasedTypes.ENV_CHANGE)
                if pool_alerts_map.get(resource_pool):
                    for alert_id in pool_alerts_map[resource_pool]:
                        meta['alert_id'] = alert_id
                        self.publish_activities_task(
                            org_id, item_id, 'resource', task_type, meta,
                            'alert.violation.env_change')
                else:
                    self.publish_activities_task(
                        org_id, item_id, 'resource', task_type, meta,
                        'alert.violation.env_change')
        r = self.resources_collection.update_one(
            filter={
                '_id': item_id,
                'deleted_at': 0
            },
            update={'$set': kwargs}
        )
        if not r.matched_count:
            raise NotFoundException(Err.OE0002, ['Resource', item_id])
        return self.get(item_id)

    def list(self, include_deleted=False, include_subresources=True, **kwargs):
        match_filter = []
        cloud_account_id = kwargs.get('cloud_account_id')
        check_ca = kwargs.pop('check_cloud_account', False)
        if check_ca and cloud_account_id:
            self._check_cloud_account_exists(cloud_account_id)
        for k in ['organization_id', 'cloud_account_id']:
            if k in kwargs.keys():
                if not match_filter:
                    match_filter.append({'$or': []})
                v = kwargs.pop(k)
                match_filter[0]['$or'].append(
                    {k: {'$in': v if isinstance(v, list) else [v]}})
        cloud_resource_id = kwargs.get('cloud_resource_id')
        if cloud_resource_id and cloud_account_id and isinstance(cloud_account_id, str):
            cloud_account = self.session.query(CloudAccount).filter(
                CloudAccount.id == cloud_account_id
            ).one_or_none()
            if cloud_account.type == CloudTypes.AZURE_CNR:
                kwargs['cloud_resource_id'] = cloud_resource_id.lower()
        for k, v in kwargs.items():
            match_filter.append(
                {k: {'$in': v if isinstance(v, list) else [v]}})
        pipeline = [
            {
                '$match': {
                    '$and': match_filter
                }
            }
        ]
        if not include_deleted:
            pipeline[0]['$match']['$and'].append({'deleted_at': 0})
        if not include_subresources:
            pipeline[0]['$match']['$and'].append({'cluster_id': {'$exists': False}})
        result = list(self.resources_collection.aggregate(pipeline))
        for r in result:
            self.format_resource(r)
        return result

    @staticmethod
    def _validate_resource_meta(meta, expected_fields):
        if expected_fields:
            unexpected_params = set()
            for field in meta:
                if field not in expected_fields:
                    unexpected_params.add(field)
            if unexpected_params:
                unexpected_params = ', '.join(unexpected_params)
                raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    def check_restrictions(self, is_new=True, **kwargs):
        rp, ip, op, msp = self.get_validation_parameters(
            kwargs.get('resource_type'))
        required_params = rp
        immutable_params = ip
        optional_params = op
        model_specific_params = msp
        extra_params = set()
        if is_new:
            extra_params.update(model_specific_params)
            for field in required_params:
                max_len = 512 if field == 'cloud_resource_id' else 255
                val = kwargs.get(field)
                if val is None:
                    raise WrongArgumentsException(Err.OE0216, [field])
                check_string_attribute(field, val, max_length=max_len)
        else:
            immutable_params.update(required_params)
        for field in optional_params:
            value = kwargs.get(field)
            if value is None:
                continue
            if field in {'meta', 'tags', 'env_properties'}:
                if value:
                    check_dict_attribute(field, value)
            elif field in {'first_seen', 'last_seen', 'cloud_created_at'}:
                check_int_attribute(field, value)
            elif field in {'is_environment', 'active', 'ssh_only'}:
                check_bool_attribute(field, value)
            elif field == 'shareable':
                check_bool_attribute(field, value)
                if value:
                    raise WrongArgumentsException(Err.OE0479, [field])
            elif field == 'name':
                check_string_attribute(field, value, max_length=512)
            else:
                check_string_attribute(field, value)
        immutables_matches = set(filter(lambda x: x in kwargs,
                                        immutable_params))
        if immutables_matches:
            raise WrongArgumentsException(
                Err.OE0211, [immutables_matches.pop()])

        all_fields = (required_params | immutable_params |
                      optional_params)
        unexpected_params = list(filter(lambda x: x not in all_fields,
                                        kwargs.keys()))
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])
        meta = kwargs.get('meta')
        if meta:
            self._validate_resource_meta(meta, extra_params)

    def check_entity_exists(self, entity_id, model):
        ent_exists = self.session.query(exists().where(
            and_((model.id == entity_id), model.deleted.is_(False)))).scalar()
        if not ent_exists:
            raise WrongArgumentsException(
                Err.OE0002, [model.__name__, entity_id])

    def get_owner(self, resource_id):
        resource = self.get(resource_id)
        if not resource:
            raise NotFoundException(
                Err.OE0002, ['Resource', resource_id])
        employee_id = resource.get('employee_id')
        employee = EmployeeController(
            self.session, self._config, self.token).get(employee_id)
        if not employee:
            raise NotFoundException(
                Err.OE0002, [Employee.__name__, employee_id])
        return employee.auth_user_id

    def _is_valid_pool(self, pool, organization_id):
        pools_tree = PoolController(
            self.session, self._config, self.token
        ).get_organization_pools(organization_id)
        if any(filter(lambda x: x['id'] == pool.id,
                      pools_tree)):
            return True
        return False

    def get_summary(self, resource, dependent_ids, expense_ctrl):
        if dependent_ids:
            summaries = expense_ctrl.get_resource_expense_summary(
                dependent_ids, join_traffic_expenses=True)
            created_at_dt = datetime.fromtimestamp(resource['created_at'])
            summary = {
                '_id': {
                    'resource_id': resource['id'],
                },
                'total_cost': 0,
                'mindate': created_at_dt,
                'maxdate': created_at_dt,
                'resource_id': resource['id'],
                'cloud_resource_id': resource['cloud_resource_id'],
                'total_traffic_expenses': 0,
                'total_traffic_usage': 0
            }
            for dependent_summary in summaries.values():
                if dependent_summary.get('mindate'):
                    summary['mindate'] = min(summary['mindate'],
                                             dependent_summary['mindate'])
                if dependent_summary.get('maxdate'):
                    summary['maxdate'] = max(summary['maxdate'],
                                             dependent_summary['maxdate'])
                summary['total_cost'] += dependent_summary.get('total_cost')
                summary['total_traffic_expenses'] += dependent_summary.get(
                    'total_traffic_expenses', 0)
                summary['total_traffic_usage'] += dependent_summary.get(
                    'total_traffic_usage', 0)
        else:
            summary = expense_ctrl.get_resource_expense_summary(
                [resource['id']], join_traffic_expenses=True
            ).get(resource['id'], {})
        return summary

    def _get_active_resource_bookings(self, resource):
        bookings_list = []
        now = datetime.utcnow()
        bookings = self.session.query(ShareableBooking).filter(and_(
            ShareableBooking.resource_id == resource['id'],
            ShareableBooking.deleted_at == 0, or_(
                ShareableBooking.released_at > int(now.timestamp()),
                ShareableBooking.released_at == 0))).all()
        if bookings:
            for booking in bookings:
                booking_dict = booking.to_dict()
                acquired_by_id = booking_dict.pop('acquired_by_id')
                booking_dict['acquired_by'] = {
                    'id': acquired_by_id,
                    'name': booking.acquired_by.name}
                bookings_list.append(booking_dict)
        return bookings_list

    def get_resource_details(self, resource):
        now = datetime.utcnow()
        cloud_account = self.session.query(CloudAccount).filter(
            CloudAccount.id == resource.get('cloud_account_id')
        ).one_or_none()
        pool_employee_set = self.session.query(
            Pool, Employee
        ).outerjoin(
            Employee, and_(Employee.id == resource.get('employee_id'))
        ).filter(
            Pool.id == resource.get('pool_id')
        ).one_or_none()
        pool, employee = None, None
        if pool_employee_set is not None:
            pool, employee = pool_employee_set

        dependent_ids = list(map(
            lambda r: r['id'], resource.get('sub_resources', [])))
        expense_ctrl = ExpenseController(self._config)
        summary = self.get_summary(resource, dependent_ids, expense_ctrl)
        this_month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        expenses = expense_ctrl.get_expenses(
            'resource_id', dependent_ids + [resource['id']],
            last_month_start, now)

        cost = 0
        month_cost = 0
        for expense in expenses:
            cost += expense['cost']
            if expense['_id']['date'] >= this_month_start:
                month_cost += expense['cost']
        employee_name = employee.name if employee else None
        min_date = summary.get('mindate')
        created_at = resource.get('created_at')
        last_seen = resource.get('last_seen')
        first_seen = int(min_date.timestamp() if min_date else created_at)
        if pool:
            pool_name = pool.name
            policies_set = self.session.query(
                PoolPolicy
            ).filter(and_(
                PoolPolicy.pool_id == pool.id,
                PoolPolicy.deleted.is_(False)
            )).all()
            policies = {
                policy.type.value: policy.to_dict() for policy in policies_set
            }
            for policy_type, policy in policies.items():
                if policy_type == 'ttl':
                    policy['limit'] = policy['limit'] if policy['limit'] == 0 else policy['limit'] * 3600 + first_seen
                    policies[policy_type] = policy
            pool_purpose = pool.purpose.value
        else:
            pool_name = None
            policies = {}
            pool_purpose = None
        last_seen = last_seen or created_at
        active = True
        if not resource.get('active', False):
            active = False
            maxdate = summary.get('maxdate')
            last_seen = maxdate.timestamp() if maxdate else created_at
        constraints_set = self.session.query(
            ResourceConstraint
        ).filter(and_(
            ResourceConstraint.resource_id == resource['id'],
            ResourceConstraint.deleted.is_(False)
        )).all()
        constraints = {
            constraint.type.value:
                constraint.to_dict() for constraint in constraints_set
        }
        bookings_list = []
        env_props_collector_link = None
        if resource.get('shareable'):
            bookings_list = self._get_active_resource_bookings(resource)
            public_ip = self._config.public_ip()
            env_props_collector_link = f"https://{public_ip}/restapi/v2/" \
                                       f"cloud_resources/{resource['id']}/" \
                                       f"env_properties_collector"
        forecast = expense_ctrl.get_monthly_forecast(
            cost, month_cost, datetime.fromtimestamp(
                first_seen)) if active else month_cost
        return {
            'cloud_type': getattr(
                getattr(cloud_account, 'type', None), 'value', None),
            'cloud_name': getattr(cloud_account, 'name', None),
            'total_cost': summary.get('total_cost', 0),
            'cost': month_cost,
            'forecast': forecast,
            'service_name': summary.get('service_name'),
            'region': summary.get('region'),
            'pool_name': pool_name,
            'pool_purpose': pool_purpose,
            'owner_name': employee_name,
            'last_seen': int(last_seen),
            'first_seen': int(first_seen),
            'active': active,
            'policies': policies,
            'constraints': constraints,
            'shareable_bookings': bookings_list,
            'env_properties_collector_link': env_props_collector_link,
            'total_traffic_expenses': summary.get('total_traffic_expenses', 0),
            'total_traffic_usage': summary.get('total_traffic_usage', 0)
        }

    def create(self, **kwargs):
        self._check_cloud_account_exists(kwargs['cloud_account_id'])
        result = self.save_bulk(
            cloud_account_id=kwargs['cloud_account_id'],
            behavior='error_existing',
            return_resources=True,
            resources=[kwargs]
        )
        return result[0]

    def get_resources(
            self, cloud_account_id, cloud_resource_ids, include_deleted=True):
        if not cloud_resource_ids:
            return []
        cond_list = [{
            'cloud_resource_id': {'$in': cloud_resource_ids}},
            {'cloud_account_id': cloud_account_id}]
        if not include_deleted:
            cond_list.append({'deleted_at': 0})
        resources = self.resources_collection.aggregate([
            {
                '$match': {
                    '$and': cond_list
                }
            }
        ])
        return list(resources)

    def _set_instance_status_date_fields(self, resource, db_resource):
        status_field = 'stopped_allocated'
        meta = db_resource.get('meta', {})
        if not resource.get('meta'):
            resource['meta'] = {}
        status_field_value = resource['meta'].get(status_field)
        default_status_value = meta.get(status_field, False)
        enable_switch = True
        if status_field_value is None:
            status_field_value = default_status_value
            enable_switch = status_field_value
            resource['meta'][status_field] = status_field_value
        if enable_switch:
            status_field_value = not status_field_value
        self._set_resource_date('last_seen_not_stopped', meta, resource,
                                status_field_value)

    def _set_volume_status_date_fields(self, resource, db_resource):
        status_field = 'attached'
        meta = db_resource.get('meta', {})
        status_field_value = resource.get('meta', {}).get(status_field)
        self._set_resource_date('last_attached', meta, resource,
                                status_field_value)

    def _set_ip_address_updated_fields(self, resource, db_resource):
        status_field = 'available'
        meta = db_resource.get('meta', {})
        if not resource.get('meta'):
            resource['meta'] = {}
        if not resource['meta'].get(status_field):
            resource['meta'][status_field] = next(
                (x for x in [resource.get('meta', {}).get(status_field),
                             meta.get(status_field), False] if x is not None), False)
        status_field_value = resource.get('meta', {}).get(status_field)
        self._set_resource_date('last_used', meta, resource,
                                not status_field_value)

    @staticmethod
    def _set_resource_date(date_field, meta, resource, status_field_value):
        if status_field_value:
            date_value = int(datetime.utcnow().timestamp())
        else:
            date_value = meta.get(date_field, 0)
        if not resource.get('meta'):
            resource['meta'] = {}
        resource['meta'][date_field] = date_value

    def split_changes(self, resource, db_resource, behavior, is_report_import):
        changed, unchanged = {}, {}
        db_first_seen = db_resource.get(
            'first_seen', resource.get('created_at'))
        db_last_seen = db_resource.get(
            'last_seen', resource.get('created_at'))
        for service_field, default_value in {
            'service_name': None,
            'first_seen': db_first_seen, 'last_seen': db_last_seen
        }.items():
            value = resource.pop(service_field, default_value)
            if value and value != db_resource.get(service_field):
                changed[service_field] = value
        resource_tags = resource.pop('tags', {})
        meta = resource.pop('meta', None) or {}
        meta = {k: v for k, v in meta.items()
                if v is not None}
        os = meta.pop('os', None)
        preinstalled = meta.pop('preinstalled', None)
        db_meta = db_resource.pop('meta', {})

        if os:
            db_meta['os'] = os
        if preinstalled:
            db_meta['preinstalled'] = preinstalled
        if behavior in ['update_existing', 'error_existing']:
            db_meta.update(meta)
        if db_meta:
            changed['meta'] = db_meta

        if behavior == 'update_existing':
            split_fields = self.get_split_fields()
            for field, value in resource.items():
                if (field in split_fields and field != 'meta' or
                        value == db_resource.get(field)):
                    unchanged[field] = db_resource.get(field) if db_resource else value
                elif field != 'meta':
                    changed[field] = value
        elif behavior == 'error_existing':
            unchanged = resource
            unchanged.update(changed)
        else:
            unchanged = resource

        db_tags = db_resource.get('tags', {}).copy()
        resource_tags = update_tags(db_tags, resource_tags, is_report_import)
        if db_resource:
            changed.update({'tags': resource_tags})
        else:
            unchanged.update({'tags': resource_tags})
        return changed, unchanged

    @staticmethod
    def gen_cloud_resource_ids(resources):
        return resources

    def extend_payload(self, resource, now):
        defaults = {
            '_id': str(uuid.uuid4()),
            'created_at': now,
            'deleted_at': 0,
        }
        resource.update(defaults)
        return resource

    def check_env_properties(
            self, resources, new_environment=False, behavior=None):
        if not new_environment or not behavior == 'error_existing':
            env_props_resources = [x for x in resources if x.get(
                'env_properties') is not None]
            if env_props_resources:
                raise WrongArgumentsException(Err.OE0212, ['env_properties'])

    def save_bulk(self, cloud_account_id, resources, behavior, return_resources,
                  is_report_import=False, new_environment=False):
        self.check_env_properties(resources, new_environment, behavior)
        rac = RuleApplyController(self.session, self._config, self.token)
        cloud_account_map, employee_allowed_pools = rac.collect_relations(
            [cloud_account_id])
        cloud_account = cloud_account_map[cloud_account_id]
        rules = rac.get_valid_rules(cloud_account.organization_id,
                                    employee_allowed_pools)
        resources = self.gen_cloud_resource_ids(resources)
        cloud_resources_ids = list(filter(
            lambda x: x is not None,
            map(lambda y: y.get('cloud_resource_id'), resources)))
        include_deleted = False if behavior == 'error_existing' else True
        db_resources_map = {
            r['cloud_resource_id']: r for r in
            self.get_resources(
                cloud_account_id, cloud_resources_ids, include_deleted)}
        not_active_envs = [
            r for _, r in db_resources_map.items()
            if (r['resource_type'] == ResourceTypes.instance.value and
                r['deleted_at'] == 0 and r.get('shareable') and
                not r.get('active'))]
        if not_active_envs:
            pool_ids = set(x['pool_id'] for x in not_active_envs)
            pool_alerts_map = PoolAlertController(
                self.session, self._config, self.token).get_pool_alerts_map(
                pool_ids, ThresholdBasedTypes.ENV_CHANGE)
            for resource in not_active_envs:
                pool_id = resource['pool_id']
                meta = {
                    'previous_state': 'Not Active',
                    'new_state': 'Active'
                }
                if pool_alerts_map.get(pool_id):
                    for alert_id in pool_alerts_map[pool_id]:
                        meta['alert_id'] = alert_id
                        self.publish_activities_task(
                            cloud_account.organization_id, resource['_id'],
                            'resource', 'env_active_state_changed', meta,
                            'alert.violation.env_change')
                else:
                    self.publish_activities_task(
                        cloud_account.organization_id, resource['_id'],
                        'resource', 'env_active_state_changed', meta,
                        'alert.violation.env_change')

        now = int(datetime.utcnow().timestamp())
        ctc = ClusterTypeController(self.session, self._config, self.token)
        resource_cluster_map = ctc.bind_clusters(
            cloud_account.organization_id, resources, db_resources_map, rules,
            is_report_import, now)

        updates_bulk = []
        insertions_bulk = []
        resource_events = {}
        # will save new inserted resource ids for error rollback,
        # not to remove existing resources on bulk_write error
        newly_discovered_resources = {}
        for resource in resources:
            if not resource.get('cloud_account_id'):
                resource['cloud_account_id'] = cloud_account_id
            self.check_restrictions(**resource)
            resource = self.extend_payload(resource, now)

            cluster = resource_cluster_map.get(
                resource.get('cloud_resource_id'))
            if cluster:
                resource['cluster_id'] = cluster['_id']
                # use cluster assignment or clear direct
                resource['pool_id'] = cluster.get('pool_id')
                resource['employee_id'] = cluster.get('employee_id')
                resource['applied_rules'] = cluster.get('applied_rules', [])
            else:
                resource, events = rac.handle_assignment_data(
                    cloud_account.organization_id, resource, cloud_account,
                    employee_allowed_pools, rules)
                resource_events[resource['_id']] = events

            tags = encoded_tags(resource.get('tags'))
            if tags:
                resource['tags'] = tags

            db_resource = db_resources_map.get(
                resource['cloud_resource_id'], {})
            if not db_resource:
                newly_discovered_resources.update({resource['_id']: resource})

            set_status_func = self.get_set_status_func(resource.get('resource_type'))
            if set_status_func:
                set_status_func(resource, db_resource)

            update, insertion = self.split_changes(
                resource, db_resource, behavior, is_report_import)
            updates_bulk.append(update)
            insertions_bulk.append(insertion)

        updated_ids = []
        if behavior in {'skip_existing', 'update_existing'}:
            update_operations = []
            filter_fields = ['cloud_resource_id', 'cloud_account_id', 'organization_id']
            field_op_map = {
                'first_seen': '$min',
                'last_seen': '$max'
            }
            for update, insertion in zip(updates_bulk, insertions_bulk):
                op_details = {}
                for field, op in field_op_map.items():
                    val = update.pop(field, None)
                    if val is not None:
                        op_details[op] = {field: val}
                for cmd, data in {'$set': update, '$setOnInsert': insertion}.items():
                    if data:
                        op_details[cmd] = {k: v for k, v in data.items()}
                update_operations.append(UpdateOne(
                    filter={
                        k: insertion[k] for k in filter_fields if insertion.get(k)
                    },
                    update=op_details,
                    upsert=True,
                ))

            try:
                write_result = retry_mongo_upsert(
                    self.resources_collection.bulk_write, update_operations)
                updated_ids = list(write_result.upserted_ids.values())
                inserted_ids = list(
                    set(updated_ids) - set(
                        [res['_id'] for res in db_resources_map.values()]))
                duplicates = list(filter(lambda x: x not in updated_ids,
                                         resource_events.keys()))
                for k in duplicates:
                    resource_events.pop(k, None)
            except Exception as exc:
                self.resources_collection.delete_many(
                    {'_id': {'$in': list(newly_discovered_resources.keys())}})
                if hasattr(exc, 'details'):
                    LOG.error('Mongo exception details: %s', exc.details)
                raise
        else:
            try:
                inserted_ids = self.resources_collection.insert_many(
                    insertions_bulk).inserted_ids
                if new_environment:
                    env_props_resources = [x for x in resources if x.get(
                        'env_properties') is not None]
                    for env_res in env_props_resources:
                        self.update_history_properties(
                            env_res, env_res.get('env_properties'),
                            new_environment)
            except BulkWriteError as ex:
                self.resources_collection.delete_many(
                    {'_id': {'$in': list(map(lambda x: x['_id'], insertions_bulk))}})
                raise WrongArgumentsException(Err.OE0003, [str(ex)])

        if resource_events:
            for events in resource_events.values():
                for event in events:
                    rac.publish_cloud_acc_activities(*event)

        if is_report_import and inserted_ids:
            newly_discovered_stat = generate_discovered_cluster_resources_stat(
                [newly_discovered_resources.get(inserted_id) for inserted_id in inserted_ids],
                resource_cluster_map,
                cluster_key='cloud_resource_id')
            for acc_id, stat in newly_discovered_stat.items():
                cloud_account = cloud_account_map[acc_id]
                meta = {
                    'object_name': cloud_account.name,
                    'stat': stat
                }
                self.publish_activities_task(
                    cloud_account.organization_id, cloud_account.id,
                    'cloud_account', 'resources_discovered', meta,
                    'cloud_account.resources_discovered', add_token=True)

        if return_resources:
            resources = self.get_resources(
                cloud_account_id, cloud_resources_ids, include_deleted)
            for resource in resources:
                self.format_resource(
                    resource, is_report_import=is_report_import)
            return resources

    def delete(self, item_id):
        r = self.resources_collection.update_one(
            filter={
                '_id': item_id
            },
            update={'$set': {'deleted_at': int(datetime.utcnow().timestamp())}}
        )
        if not r.modified_count:
            raise NotFoundException(Err.OE0002, ['Resource', item_id])

    def delete_cloud_resources(self, cloud_account_id):
        now = int(datetime.utcnow().timestamp())
        chunk_size = 10000
        while True:
            res = self.resources_collection.find(
                {'cloud_account_id': cloud_account_id, 'deleted_at': 0},
                {'_id': True}).limit(chunk_size)
            res_ids = [x['_id'] for x in res]
            if not len(res_ids):
                break
            r = self.resources_collection.update_many(
                filter={
                    '_id': {'$in': res_ids}
                },
                update={
                    '$set': {'deleted_at': now},
                    '$unset': {'cluster_id': ''}
                }
            )
            if r.modified_count != len(res_ids):
                LOG.warning('Delete cloud resources failed - deleted %d of %d;'
                            ' result: %s' %
                            (r.modified_count, len(res_ids), r.raw_result))

    def get_script(self, item_id):
        resource = self.get(item_id)
        if not resource.get('shareable'):
            raise WrongArgumentsException(Err.OE0480, ['Resource', item_id])
        public_ip = self._config.public_ip()
        base_script = "#!/bin/bash\ncurl --request POST -d '{\"your_field\":" \
                      " \"$FIELD_VAR\", \"other_field\": \"$OTHER_VAR\"}' " \
                      "\"https://%s/restapi/v2/cloud_resources/%s/" \
                      "env_properties_collector\""
        return base_script % (public_ip, item_id)

    def update_history_properties(
            self, resource, properties, new_environment=False):
        if not isinstance(properties, dict):
            raise WrongArgumentsException(Err.OE0344, ['Properties'])
        for key in properties.keys():
            if not isinstance(key, str):
                raise WrongArgumentsException(
                    Err.OE0214, ['Properties key % key' % key])
        old_properties = {} if new_environment else resource.get('env_properties', {})
        new_properties = dict(old_properties, **properties)
        for key, value in dict(new_properties).items():
            if value is None:
                del new_properties[key]
        changes = {}
        for key, value in properties.items():
            old_value = old_properties.get(key)
            changes[key] = {'old': old_value, 'new': value}
        try:
            resource_id = resource['id'] if resource.get(
                'id') else resource['_id']
            self.property_history_collection.insert_one({
                'resource_id': resource_id,
                'time': int(datetime.utcnow().timestamp()),
                'changes': changes
            })
        except BulkWriteError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return new_properties

    def get_history(self, item_id, start_date=None, end_date=None):
        resource = self.get(item_id)
        if not resource.get('shareable'):
            raise WrongArgumentsException(Err.OE0480, ['Resource', item_id])
        filter_cond = {'resource_id': item_id}
        time_cond = {}
        if start_date:
            time_cond['$gte'] = start_date
        if end_date:
            time_cond['$lte'] = end_date
        if time_cond:
            filter_cond['time'] = time_cond
        res = self.property_history_collection.find(
            filter_cond, {'_id': False}).sort('time')
        return resource.get('name', resource.get('cloud_resource_id')), list(res)


class CloudResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CloudResourceController
