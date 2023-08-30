from datetime import datetime
from optscale_client.herald_client.client_v2 import Client as HeraldClient
import logging
import json
from kombu.pools import producers
from kombu import Connection as QConnection, Exchange
import requests
from tools.cloud_adapter.model import ResourceTypes
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, NotFoundException, ForbiddenException)
from rest_api.rest_api_server.controllers.base import (BaseController, MongoMixin,
                                                       ResourceFormatMixin)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.cloud_account import CloudAccountController
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.organization import OrganizationController
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.controllers.ssh_key import SshKeyController
from rest_api.rest_api_server.controllers.calendar_synchronization import (
    CalendarSynchronizationController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    Employee, Organization, ShareableBooking, Pool, JiraIssueAttachment)
from rest_api.rest_api_server.utils import (check_int_attribute,
                                            raise_not_provided_exception,
                                            CURRENCY_MAP)
from sqlalchemy import or_, and_, false
from sqlalchemy.exc import IntegrityError

LOG = logging.getLogger(__name__)
ROUTING_KEY = 'booking-activity'
EXCHANGE_NAME = 'booking-activities'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


class ShareableBookingController(BaseController, MongoMixin,
                                 ResourceFormatMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._cloud_resource_ctrl = None

    @property
    def cloud_resource_ctrl(self):
        if self._cloud_resource_ctrl is None:
            self._cloud_resource_ctrl = CloudResourceController(
                self.session, self._config, self.token)
        return self._cloud_resource_ctrl

    def _get_model_type(self):
        return ShareableBooking

    def get_organization(self, organization_id):
        organization = OrganizationController(
            self.session, self._config, self.token).get(organization_id)
        if organization is None:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])
        return organization

    def _check_employee(self, acquired_by_id, organization_id):
        if acquired_by_id is None:
            raise_not_provided_exception('acquired_by_id')
        else:
            owner = EmployeeController(
                self.session, self._config, self.token).get(
                acquired_by_id, organization_id=organization_id)
            if owner is None:
                raise NotFoundException(Err.OE0002, [Employee.__name__,
                                                     acquired_by_id])
            return owner

    def _check_cluster(self, organization_id, cluster):
        cluster_org_id = cluster.get('organization_id')
        if organization_id != cluster_org_id:
            raise WrongArgumentsException(Err.OE0454,
                                          ['Cluster', cluster['id']])
        if not cluster.get('shareable'):
            raise WrongArgumentsException(Err.OE0480, ['Cluster',
                                                       cluster['id']])

    def _check_resource(self, resource, organization_id=None):
        cloud_account_id = resource.get('cloud_account_id')
        cloud_account = CloudAccountController(self.session, self._config,
                                               self.token).get(cloud_account_id)
        if organization_id and cloud_account.organization_id != organization_id:
            raise WrongArgumentsException(Err.OE0454,
                                          ['Resource', resource['id']])
        resource_type = resource.get('resource_type')
        is_environment = resource.get('is_environment', False)
        if not is_environment and resource_type != 'Instance':
            raise WrongArgumentsException(Err.OE0384, [resource_type])
        if not resource.get('shareable'):
            raise WrongArgumentsException(Err.OE0480, ['Resource',
                                                       resource['id']])
        if resource.get('cluster_id'):
            raise WrongArgumentsException(Err.OE0481, [resource['id']])

    def _check_resource_param(self, organization_id, resource_id):
        resource = self.cloud_resource_ctrl.get(resource_id)
        if resource.get('cluster_type_id'):
            self._check_cluster(organization_id, resource)
        else:
            self._check_resource(resource, organization_id)
        return resource

    def _check_ssh_key(self, ssh_key_id, employee, resource):
        if not ssh_key_id:
            if resource.get('ssh_only'):
                raise WrongArgumentsException(Err.OE0216, ['ssh_key_id'])
            return
        ssh_key = SshKeyController(
            self.session, self._config, self.token
        ).get(ssh_key_id)
        if not ssh_key:
            raise NotFoundException(Err.OE0002, ['ssh_key', ssh_key_id])
        if ssh_key.employee_id != employee.id:
            raise WrongArgumentsException(Err.OE0510,
                                          [ssh_key_id, employee.id])
        user_id = self.get_user_id()
        if user_id != employee.auth_user_id:
            if not ssh_key.default:
                raise WrongArgumentsException(Err.OE0511, [])
        return ssh_key

    @staticmethod
    def _check_dates(acquired_since, released_at):
        if released_at is not None and acquired_since is not None and (
                acquired_since > released_at != 0):
            raise WrongArgumentsException(Err.OE0446, ['released_at',
                                                       'acquired_since'])

    def _check_slots_with_existing(self, resource_id, acquired_since,
                                   released_at):
        if not released_at:
            released_at = 0
        if not acquired_since:
            acquired_since = int(datetime.utcnow().timestamp())
        shareable_bookings = self.session.query(
            ShareableBooking).filter(
            ShareableBooking.resource_id == resource_id,
            ShareableBooking.deleted.is_(False)
        ).all()
        for booking in shareable_bookings:
            if booking.is_active(acquired_since):
                # acquired_since in [booking.acquired_since; booking.released_at)
                raise WrongArgumentsException(Err.OE0482, [])
            if (acquired_since < booking.acquired_since and (
                    released_at == 0 or released_at > booking.acquired_since)):
                raise WrongArgumentsException(Err.OE0482, [])

    def contains_shareable_resource(self, organization_id):
        cloud_accounts = CloudAccountController(
            self.session, self._config, self.token).list(
            organization_id=organization_id)
        cloud_acc_ids = list(x['id'] for x in cloud_accounts)
        shareable_resource_filter = {
            '$or': [
                {'cloud_account_id': {'$in': cloud_acc_ids}},
                {'organization_id': organization_id}
            ],
            'shareable': True,
            'deleted_at': 0
        }
        return bool(self.resources_collection.count_documents(
            shareable_resource_filter))

    def send_first_shareable_email(self, organization_id, count=1):
        organization = self.session.query(Organization).filter(and_(
            Organization.id == organization_id,
            Organization.deleted.is_(False),
            Organization.is_demo.is_(false())
        )).one_or_none()
        if organization is None:
            return
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return
        template_params = {
            'texts': {
                'organization': {
                    'id': organization.id,
                    'name': organization.name,
                    'currency_code': CURRENCY_MAP.get(organization.currency, '$')
                },
                'title': "First shareable resource",
                'shareable_resource_count': count
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], 'OptScale shareable resources notification',
            template_type="first_shareable_resources",
            template_params=template_params)

    @staticmethod
    def split_resources_by_shareability(resources):
        # only instances, clusters and environments can be shareable
        instances_clusters = []
        not_instances_clusters = []
        already_shareable = []
        for res in resources:
            if res.get('shareable'):
                already_shareable.append(res)
            elif (res['resource_type'] == ResourceTypes.instance.value and
                  not res.get('cluster_id')) or res.get('cluster_type_id'):
                instances_clusters.append(res)
            else:
                not_instances_clusters.append(res)
        return instances_clusters, not_instances_clusters, already_shareable

    def _check_resources(self, organization_id, resource_ids):
        cloud_accounts = CloudAccountController(
            self.session, self._config, self.token).list(
            organization_id=organization_id)
        cloud_accs = set(x['id'] for x in cloud_accounts)
        all_resources = self.cloud_resource_ctrl.list(
            _id=resource_ids, include_deleted=True)
        resources = []
        invalid_resources = []
        not_active_resources = []
        all_resources_ids = set(x['id'] for x in all_resources)
        not_found_resources_ids = [x for x in resource_ids
                                   if x not in all_resources_ids]
        for resource in all_resources:
            if (resource['deleted_at'] != 0 or
                    resource.get('cloud_account_id') and
                    resource.get('cloud_account_id') not in cloud_accs):
                invalid_resources.append(resource)
            elif resource.get('shareable'):
                resources.append(resource)
            elif not resource.get('active'):
                not_active_resources.append(resource)
            else:
                resources.append(resource)
        if not_found_resources_ids:
            for res_id in not_found_resources_ids:
                invalid_resources.append({'id': res_id,
                                          'cloud_resource_id': res_id})
        return resources, invalid_resources, not_active_resources

    def get_employee_by_id(self, employee_id):
        employee = self.session.query(Employee).filter(and_(
            Employee.id == employee_id,
            Employee.deleted.is_(False)
        )).one_or_none()
        if employee is None:
            raise NotFoundException(Err.OE0002,
                                    [Employee.__name__, employee_id])
        return employee

    def check_employee_permission(self, employee, resource_id):
        user_id = self.get_user_id()
        if user_id == employee.auth_user_id:
            return
        required_permission = 'BOOK_ENVIRONMENTS'
        try:
            code, response = self.auth_client.authorize_user_list(
                users=[employee.auth_user_id], actions=[required_permission],
                scope_type='cloud_resource', scope_id=resource_id)
        except requests.exceptions.HTTPError as ex:
            raise WrongArgumentsException(Err.OE0435, [str(ex)])
        if required_permission not in response.get(employee.auth_user_id, []):
            raise ForbiddenException(Err.OE0505, [employee.name, employee.id])

    def create(self, **kwargs):
        org_id = kwargs.get('organization_id')
        is_admin_permission = kwargs.pop('is_admin_permission', False)
        self.get_organization(org_id)
        acquired_by_id = kwargs.get('acquired_by_id')
        employee = self._check_employee(acquired_by_id, org_id)
        ssh_key_id = kwargs.pop('ssh_key_id', None)
        self.check_create_restrictions(**kwargs)
        resource_id = kwargs.get('resource_id')
        self.check_employee_permission(employee, resource_id)
        resource = self._check_resource_param(org_id, resource_id)
        ssh_key = self._check_ssh_key(ssh_key_id, employee, resource)
        if ssh_key:
            kwargs.update({'ssh_key': json.dumps(ssh_key.to_dict())})
        shareable_book = ShareableBooking(**kwargs)
        acquired_since = kwargs.get('acquired_since')
        released_at = kwargs.get('released_at')
        self._check_dates(acquired_since, released_at)
        self._check_slots_with_existing(resource_id, acquired_since,
                                        released_at)
        now_ts = int(datetime.utcnow().timestamp())
        if (is_admin_permission is False and acquired_since is not None and
                acquired_since < now_ts):
            raise ForbiddenException(Err.OE0495, [])
        self.session.add(shareable_book)
        self.create_calendar_event(shareable_book)
        try:
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])

        return self.fill_booking_acquired_by(shareable_book)

    def get_resource_current_booking(self, resource_id):
        now_ts = int(datetime.utcnow().timestamp())
        resource_booking = self.session.query(ShareableBooking).filter(
            and_(ShareableBooking.resource_id == resource_id,
                 ShareableBooking.acquired_since <= now_ts,
                 ShareableBooking.deleted_at == 0,
                 or_(ShareableBooking.released_at == 0,
                     ShareableBooking.released_at >= now_ts))).one_or_none()
        if resource_booking:
            booking = self.fill_booking_acquired_by(resource_booking)
            return booking

    def get_upcoming_booking(self, resource_id, current_booking=None):
        acquired_since = int(datetime.utcnow().timestamp())
        if current_booking and current_booking.get('released_at'):
            acquired_since = current_booking['released_at']
        resource_bookings = self.session.query(ShareableBooking).filter(
            and_(ShareableBooking.resource_id == resource_id,
                 ShareableBooking.acquired_since >= acquired_since,
                 ShareableBooking.deleted_at == 0)).all()
        if resource_bookings:
            upcoming_booking = min(
                [x for x in resource_bookings], key=lambda x: x.acquired_since)
            return upcoming_booking

    def create_calendar_event(self, shareable_book):
        cal_sync_cntr = CalendarSynchronizationController(
            self.session, self._config, self.token)
        calendar_sync = cal_sync_cntr.get_by_organization_id(
            shareable_book.organization_id)
        if calendar_sync:
            return cal_sync_cntr.create_calendar_events(
                [shareable_book], calendar_sync.calendar_id)

    def delete_calendar_event(self, shareable_book):
        cal_sync_cntr = CalendarSynchronizationController(
            self.session, self._config, self.token)
        calendar_sync = cal_sync_cntr.get_by_organization_id(
            shareable_book.organization_id)
        if calendar_sync and shareable_book.event_id:
            cal_sync_cntr.delete_calendar_event_by_id(
                calendar_sync, shareable_book.event_id)

    def update_calendar_event(self, shareable_book):
        cal_sync_cntr = CalendarSynchronizationController(
            self.session, self._config, self.token)
        calendar_sync = cal_sync_cntr.get_by_organization_id(
            shareable_book.organization_id)
        if calendar_sync and shareable_book.event_id:
            updates = {
                'end': datetime.fromtimestamp(shareable_book.released_at)
            }
            return cal_sync_cntr.update_calendar_event(
                shareable_book.event_id, calendar_sync.calendar_id, updates)

    def get_jira_issue_attachments(self, item_ids):
        attachments = self.session.query(JiraIssueAttachment).filter(
            JiraIssueAttachment.deleted.is_(False),
            JiraIssueAttachment.shareable_booking_id.in_(item_ids),
        ).all()
        return attachments

    def check_autorelease(self, item_id):
        item = self.get(item_id)
        if (item.jira_auto_release and
                not self.get_jira_issue_attachments([item.id])):
            self.release(item.id, is_admin_permission=True,
                         released_at=int(datetime.utcnow().timestamp()))

    def release(self, item_id, is_admin_permission, **kwargs):
        item = self.get(item_id)
        if not item:
            raise NotFoundException(Err.OE0002, [ShareableBooking.__name__,
                                                 item_id])
        resource = next(self.resources_collection.find(
            {'_id': item.resource_id}).limit(1))
        if not resource.get('shareable'):
            raise WrongArgumentsException(Err.OE0480, ['Resource',
                                                       resource['_id']])

        now_ts = int(datetime.utcnow().timestamp())
        released_at = kwargs.get('released_at')
        check_int_attribute('released_at', released_at)
        # only released_at param is expected
        unexpected_params = [
            p for p in kwargs.keys() if p not in ['released_at']]
        if unexpected_params:
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])
        self._check_dates(item.acquired_since, released_at)
        other_shareable_bookings = self.session.query(
            ShareableBooking).filter(
            ShareableBooking.id != item.id,
            ShareableBooking.resource_id == item.resource_id,
            ShareableBooking.acquired_since > item.acquired_since,
            ShareableBooking.deleted.is_(False),
        ).all()
        for shareable_booking in other_shareable_bookings:
            if (shareable_booking.acquired_since < released_at or
                    released_at == 0):
                raise WrongArgumentsException(Err.OE0482, [])
        is_booking_release = released_at <= now_ts
        if not is_booking_release and not is_admin_permission:
            raise ForbiddenException(Err.OE0498, [item_id])
        item.released_at = released_at
        self.update_calendar_event(item)
        self.session.add(item)
        attachments = self.get_jira_issue_attachments([item_id])
        for attachment in attachments:
            attachment.deleted_at = now_ts
        try:
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        resource_name = resource.get('name', resource.get('cloud_resource_id'))
        if released_at <= now_ts:
            self.publish_task({
                'organization_id': item.organization_id,
                'observe_time': int(datetime.utcnow().timestamp()),
                'resource': resource,
                'object_id': item.id
            })
            meta = {
                'object_name': resource_name
            }
            self.publish_activities_task(
                item.organization_id, resource['_id'], 'resource',
                'shareable_booking_released', meta,
                'resource.shareable_booking_released', add_token=True)
        else:
            meta = {
                'object_name': resource_name
            }
            self.publish_activities_task(
                item.organization_id, resource['_id'], 'resource',
                'shareable_resource_changed', meta,
                'resource.shareable_resource_changed', add_token=True)
        return item

    @staticmethod
    def fill_booking_acquired_by(booking):
        if booking:
            booking_dict = booking.to_dict()
            acquired_by_id = booking_dict.pop('acquired_by_id')
            booking_dict['acquired_by'] = {'id': acquired_by_id,
                                           'name': booking.acquired_by.name}
            return booking_dict

    def get_shareable_resources(self, organization_id):
        self.get_organization(organization_id)
        cloud_accounts = CloudAccountController(
            self.session, self._config, self.token).list(
                organization_id=organization_id)
        cloud_accounts_map = {ca['id']: ca for ca in cloud_accounts}
        res_filter = {
            '$or': [
                {'cloud_account_id': {'$in': list(cloud_accounts_map.keys())}},
                {'organization_id': organization_id}
            ],
            'shareable': True,
            'deleted_at': 0
        }
        all_resources = list(self.resources_collection.find(res_filter))
        id_resource_map = {}
        pool_ids = []
        for res in all_resources:
            id_resource_map[res['_id']] = res
            pool_id = res.get('pool_id')
            if pool_id:
                pool_ids.append(pool_id)
        pools = self.session.query(Pool).filter(
            Pool.id.in_(pool_ids),
            Pool.deleted.is_(False),
        ).all()
        pools_map = {pool.id: pool for pool in pools}
        now_ts = int(datetime.utcnow().timestamp())
        shareable_bookings = self.session.query(
            ShareableBooking).filter(
            ShareableBooking.organization_id == organization_id,
            ShareableBooking.deleted.is_(False),
            or_(
                ShareableBooking.released_at > now_ts,
                ShareableBooking.released_at == 0
            )
        ).all()
        resource_id_bookings_map = {}
        for booking in shareable_bookings:
            resource_id = booking.resource_id
            if not resource_id_bookings_map.get(resource_id):
                resource_id_bookings_map[resource_id] = []
            resource_id_bookings_map[resource_id].append(
                self.fill_booking_acquired_by(booking))
        result = []
        for resource_id, resource in id_resource_map.items():
            resource['shareable_bookings'] = resource_id_bookings_map.get(
                resource_id, [])
            resource_result = self.format_resource(
                resource, ignore_dependencies=True)
            cloud_account_id = resource.get('cloud_account_id')
            if cloud_account_id:
                resource_result['cloud_account_name'] = cloud_accounts_map[
                    cloud_account_id]['name']
                resource_result['cloud_account_type'] = cloud_accounts_map[
                    cloud_account_id]['type']
            pool_id = resource.get('pool_id')
            if pool_id:
                pool = pools_map[pool_id]
                resource_result['pool_name'] = pool.name
                resource_result['pool_purpose'] = pool.purpose.value
            result.append(resource_result)
        return result

    def get_resource_bookings(self, resource_id):
        resource = self.cloud_resource_ctrl.get(resource_id)
        if resource:
            self._check_resource(resource)
        else:
            raise NotFoundException(Err.OE0002, ['Resource', resource_id])
        now_ts = int(datetime.utcnow().timestamp())
        resource_bookings = []
        bookings = self.session.query(
            ShareableBooking).filter(
            ShareableBooking.resource_id == resource_id,
            ShareableBooking.deleted.is_(False),
            or_(
                ShareableBooking.released_at > now_ts,
                ShareableBooking.released_at == 0
            )
        ).all()
        for booking in bookings:
            resource_bookings.append(self.fill_booking_acquired_by(booking))
        return resource_bookings

    def delete(self, item_id, is_admin_permission=False):
        shareable_booking = self.get(item_id)
        if not shareable_booking:
            raise NotFoundException(Err.OE0002, [ShareableBooking.__name__,
                                                 item_id])
        resource = next(self.resources_collection.find(
            {'_id': shareable_booking.resource_id}).limit(1))
        now_ts = int(datetime.utcnow().timestamp())
        # admin can delete all bookings, resource owner can delete only
        # future bookings
        if (not is_admin_permission and
                (shareable_booking.is_active(now_ts) or
                 now_ts > shareable_booking.released_at != 0)):
            raise ForbiddenException(Err.OE0484, [item_id])
        self.delete_calendar_event(shareable_booking)
        super().delete(item_id)
        meta = {
            'object_name': resource.get('name', resource.get(
                'cloud_resource_id'))
        }
        self.publish_activities_task(
            shareable_booking.organization_id, resource['_id'], 'resource',
            'shareable_resource_deleted', meta,
            'resource.shareable_resource_deleted', add_token=True)

    def publish_task(self, task_params):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)
        task_exchange = Exchange(EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task_params,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=ROUTING_KEY,
                retry=True,
                retry_policy=RETRY_POLICY
            )

    def get_shareable_bookings(self, organization_id, start_date, end_date):
        self.get_organization(organization_id)
        shareable_bookings = self.session.query(ShareableBooking).filter(
            ShareableBooking.organization_id == organization_id,
            ShareableBooking.deleted.is_(False),
            or_(
                and_(
                    ShareableBooking.released_at > start_date,
                    ShareableBooking.released_at <= end_date
                ),
                and_(
                    ShareableBooking.acquired_since > start_date,
                    ShareableBooking.acquired_since <= end_date
                )
            )
        ).all()
        return shareable_bookings


class ShareableBookingAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ShareableBookingController
