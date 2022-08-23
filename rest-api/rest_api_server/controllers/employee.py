import logging
import re
import requests
from config_client.client import etcd
from sqlalchemy import exists, and_, or_, func
from sqlalchemy.exc import IntegrityError
from optscale_exceptions.common_exc import (
    NotFoundException, ConflictException, ForbiddenException,
    UnauthorizedException, WrongArgumentsException)

from rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.expense import (
    CloudFilteredEmployeeFormattedExpenseController,
    PoolFilteredEmployeeFormattedExpenseController)
from rest_api_server.controllers.organization_constraint import OrganizationConstraintController
from rest_api_server.exceptions import Err
from rest_api_server.models.enums import (AuthenticationType,
                                          PoolPurposes, RolePurposes)
from rest_api_server.models.models import (AssignmentRequest, Employee,
                                           Organization, Pool, Rule,
                                           ShareableBooking)
from rest_api_server.utils import Config, CURRENCY_MAP

from auth_client.client_v2 import Client as AuthClient
from herald_client.client_v2 import Client as HeraldClient

LOG = logging.getLogger(__name__)


class EmployeeController(BaseController, MongoMixin):
    def _get_model_type(self):
        return Employee

    def _validate(self, item, is_new=True, **kwargs):
        org_id = kwargs.get('organization_id')
        if org_id:
            self.check_organization(kwargs.get('organization_id'))
        user_id = kwargs.get('auth_user_id')
        if user_id and is_new and self.is_employee_exists(
                org_id, auth_user_id=user_id):
            raise ConflictException(Err.OE0382, [user_id, org_id])

    def is_employee_exists(self, organization_id, auth_user_id=None,
                           employee_id=None):
        if auth_user_id:
            find_query = and_(
                self.model_type.organization_id == organization_id,
                self.model_type.auth_user_id == auth_user_id,
                self.model_type.deleted.is_(False)
            )
        elif employee_id:
            find_query = and_(
                self.model_type.organization_id == organization_id,
                self.model_type.id == employee_id,
                self.model_type.deleted.is_(False)
            )
        else:
            return False

        employee_exist = self.session.query(
            exists().where(find_query)).scalar()
        return employee_exist

    def check_organization(self, organization_id):
        org = self.session.query(Organization).filter(
            Organization.id == organization_id,
            Organization.deleted.is_(False)
        ).one_or_none()
        if org is None:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])

    def _get_organization_info(self, org_ids):
        queryset = self.session.query(Organization.id, Organization.name).filter(
            Organization.id.in_(org_ids)
        ).all()
        return dict(queryset)

    def get_org_and_pool_summary_map(self, org_id, root_pool_deleted=False):
        pools = self.session.query(
            Pool
        ).filter(
            Pool.deleted.is_(False),
            Pool.organization_id == org_id
        ).all()
        result = {
            pool.id: {
                'name': pool.name,
                'purpose': pool.purpose.value,
                'type': 'pool',
                'default_owner_id': pool.default_owner_id,
                'parent_id': pool.parent_id
            } for pool in pools
        }
        org = self.session.query(
            Organization
        ).filter(
            Organization.deleted.is_(False),
            Organization.id == org_id
        ).scalar()
        if org:
            result.update({
                org_id: {
                    'name': org.name,
                    'purpose': PoolPurposes.BUSINESS_UNIT.value,
                    'type': 'organization'
                }
            })
            if root_pool_deleted:
                result[org.pool_id] = {
                    'name': org.name,
                    'purpose': PoolPurposes.BUSINESS_UNIT.value,
                    'type': 'pool'
                }
        return result

    def _get_roles_info(self, user_ids):
        _, response = self.auth_client.user_roles_get(user_ids)
        return response

    def get_roles_info(self, user_ids, current_org_id,
                       exclude_role_purpose_list=None):
        roles_info = self._get_roles_info(user_ids)
        org_pool_summary_map = self.get_org_and_pool_summary_map(
            current_org_id)
        all_possible_ids = list(org_pool_summary_map.keys())
        result = dict()
        for i in roles_info:
            user_id = i['user_id']
            result_user_info = result.get(user_id)
            if not result_user_info:
                result[user_id] = {
                    'user_display_name': i['user_display_name'],
                    'user_email': i['user_email'],
                    'assignments': list()
                }
            if i['assignment_resource_id'] in all_possible_ids:
                if exclude_role_purpose_list and i['role_purpose'] in exclude_role_purpose_list:
                    continue
                org_pool_summary = org_pool_summary_map.get(
                    i['assignment_resource_id'], {})
                result[user_id]['assignments'].append(
                    {
                        'assignment_resource_id': i['assignment_resource_id'],
                        'role_name': i['role_name'],
                        'assignment_resource_name': org_pool_summary['name'],
                        'assignment_resource_type': org_pool_summary['type'],
                        'assignment_resource_purpose':
                            org_pool_summary['purpose'],
                        'assignment_id': i['assignment_id'],
                        'purpose': i['role_purpose']
                    })
        return result

    def _get_auth_users(self, user_ids):
        _, response = self.auth_client.user_list(user_ids)
        return response

    def _list(self, organization_id, **kwargs):
        org = self.session.query(Organization).filter(
            Organization.id == organization_id,
            Organization.deleted.is_(False)
        ).scalar()
        if org is None:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        return super().list(organization_id=org.id, **kwargs)

    def list(self, organization_id, **kwargs):
        roles = kwargs.pop('roles', None)
        exclude_myself = kwargs.pop('exclude_myself', False)
        current_only = kwargs.pop('current_only', False)
        fields = kwargs.pop('fields', [])
        user_id = None
        if not current_only:
            user_id = kwargs.pop('auth_user_id', None)
        employees = self._list(organization_id, **kwargs)
        if exclude_myself:
            employees = list(filter(
                lambda x: x.auth_user_id != user_id, employees))
        user_ids = list(
            map(lambda x: x.auth_user_id, filter(
                lambda y: y.auth_user_id is not None, employees)))
        auth_users = self._get_auth_users(user_ids) if user_ids else []
        slack_connected = {e['id']: e['slack_connected'] for e in auth_users}
        jira_connected = {e['id']: e['jira_connected'] for e in auth_users}
        result = list()
        roles_info = dict()
        if roles:
            roles_info = self.get_roles_info(
                user_ids, organization_id, [RolePurposes.optscale_member.value])
        for employee in employees:
            item = employee.to_dict()
            item.update({'slack_connected': slack_connected.get(
                item['auth_user_id'], False)})
            item.update({'jira_connected': jira_connected.get(
                item['auth_user_id'], False)})
            if roles:
                employee_role_info = roles_info.get(employee.auth_user_id)
                if not employee_role_info:
                    employee_role_info = {
                        'user_display_name': None,
                        'user_email': None,
                        'assignments': list()
                    }
                item.update(employee_role_info)
            if fields:
                existing_fields = list(item.keys())
                [item.pop(x) for x in existing_fields if x not in fields]
            result.append(item)
        return result

    def get_expenses(self, employee, start_date, end_date, filter_by):
        controller_map = {
            'cloud': CloudFilteredEmployeeFormattedExpenseController,
            'pool': PoolFilteredEmployeeFormattedExpenseController,
        }
        controller = controller_map.get(filter_by)(self.session, self._config)
        return controller.get_formatted_expenses(employee, start_date, end_date)

    def get_employee_by_user_and_organization(self, user_id,
                                              organization_id):
        employees = self._list(organization_id, auth_user_id=user_id)
        employees_count = len(employees)
        if employees_count == 0:
            raise ForbiddenException(Err.OE0378, [])
        else:
            return employees[0]

    def _get_rules(self, organization_id, employee_id):
        return self.session.query(Rule).filter(
            and_(
                Rule.deleted_at == 0,
                Rule.organization_id == organization_id,
                Rule.owner_id == employee_id
            )
        ).all()

    @staticmethod
    def is_org_manager(assignments, organization_id):
        for a in assignments:
            if (a['assignment_resource'] == organization_id and
                    a['role_name'] == 'Manager'):
                return True

    def get_org_manager_user(self, organization_id, user_not_equal):
        _, org_managers = self.auth_client.user_roles_get(
            scope_ids=[organization_id],
            role_purposes=[RolePurposes.optscale_manager.value])
        for candidate in org_managers:
            if candidate['user_id'] != user_not_equal:
                if self.is_employee_exists(organization_id,
                                           auth_user_id=candidate['user_id']):
                    return candidate['user_id']

    def _get_assignment_requests(self, employee_id):
        return self.session.query(AssignmentRequest).filter(and_(
            AssignmentRequest.deleted_at == 0,
            or_(AssignmentRequest.approver_id == employee_id,
                AssignmentRequest.requester_id == employee_id))).all()

    def _get_shareable_bookings(self, employee_id):
        return self.session.query(ShareableBooking).filter(and_(
            ShareableBooking.deleted_at == 0,
            ShareableBooking.acquired_by_id == employee_id)).all()

    def _get_pools(self, pool_ids):
        return self.session.query(Pool).filter(and_(
            Pool.deleted_at == 0,
            Pool.id.in_(pool_ids))).all()

    def _reassign_resources_to_new_owner(self, new_owner_id, employee, scopes):
        owned_pools = {pool_id: pool for pool_id, pool in scopes.items()
                       if pool.get('default_owner_id') == employee.id}
        pools = self._get_pools(list(owned_pools.keys()))
        for pool in pools:
            pool.default_owner_id = new_owner_id

        rules = self._get_rules(employee.organization_id, employee.id)
        for rule in rules:
            rule.owner_id = new_owner_id

        assignment_requests = self._get_assignment_requests(employee.id)
        for req in assignment_requests:
            if req.approver_id == employee.id:
                change_field = 'approver_id'
            else:
                change_field = 'requester_id'
            setattr(req, change_field, new_owner_id)

        self.resources_collection.update_many(filter={
            "employee_id": employee.id, "deleted_at": 0
        }, update={'$set': {'employee_id': new_owner_id}})

        bookings = self._get_shareable_bookings(employee.id)
        for booking in bookings:
            booking.acquired_by_id = new_owner_id

        try:
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])

    def delete(self, item_id, reassign_resources=True, **kwargs):
        employee = self.get(item_id)
        scopes = self.get_org_and_pool_summary_map(employee.organization_id)
        try:
            auth_client = AuthClient(
                url=Config().auth_url, token=self.token,
                secret=Config().cluster_secret)
            _, assignments = auth_client.assignment_list(employee.auth_user_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise UnauthorizedException(Err.OE0235, [])
            raise

        if reassign_resources:
            new_owner_id = kwargs.get('new_owner_id')
            user_id = kwargs.get('user_id')

            if new_owner_id:
                new_owner_emp = self.get(new_owner_id)
                if new_owner_emp and new_owner_id != employee.id:
                    _, user_assignments = self.auth_client.assignment_list(
                        new_owner_emp.auth_user_id)
                    if not self.is_org_manager(
                            user_assignments, employee.organization_id):
                        raise WrongArgumentsException(Err.OE0217, ['new_owner_id'])
                else:
                    raise WrongArgumentsException(Err.OE0217, ['new_owner_id'])
            elif user_id and user_id != employee.auth_user_id:
                user_emp = self.get_employee_by_user_and_organization(
                    user_id, employee.organization_id)
                _, user_assignments = self.auth_client.assignment_list(
                    user_id)
                new_owner_id = user_emp.id
            else:
                new_owner_user = self.get_org_manager_user(
                    employee.organization_id, employee.auth_user_id)
                if not new_owner_user:
                    raise ForbiddenException(Err.OE0497, [])
                if new_owner_user:
                    new_owner_emp = self.get_employee_by_user_and_organization(
                        new_owner_user, employee.organization_id)
                    new_owner_id = new_owner_emp.id

            if new_owner_id:
                self._reassign_resources_to_new_owner(
                    new_owner_id, employee, scopes)

        for assignment in assignments:
            if scopes.get(assignment['assignment_resource']):
                auth_client.assignment_delete(
                    id=assignment['assignment_id'],
                    user_id=employee.auth_user_id)

        OrganizationConstraintController(
            self.session, self._config, self.token).delete_constraints_with_hits(
            employee.organization_id, filters={'owner_id': item_id})

        super().delete(item_id)

    @property
    def notification_domain_blacklist(self):
        try:
            return self._config.domains_blacklist(
                blacklist_key='new_employee_email')
        except etcd.EtcdKeyNotFound:
            return []

    def send_new_employee_email(self, organization_id, organization_name,
                                currency, employee_id, user_email,
                                is_password_autogenerated=False):
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return

        for domain in self.notification_domain_blacklist:
            if domain.startswith('@'):
                domain_regex = '{}$'.format(re.escape(domain))
            else:
                domain_regex = '@{}$'.format(re.escape(domain))
            if re.search(domain_regex, user_email.lower()):
                return

        if is_password_autogenerated:
            authentication_type = AuthenticationType.GOOGLE.value
        else:
            authentication_type = AuthenticationType.PASSWORD.value

        employees_count = self.session.query(
            func.count(Employee.id)
        ).filter(and_(
            Employee.organization_id == organization_id,
            Employee.deleted.is_(False)
        )).scalar()

        subject = f'[{self._config.public_ip()}] New user joined organization'
        template_params = {
            'texts': {
                'organization': {
                    'id': organization_id,
                    'name': organization_name,
                    'currency_code': CURRENCY_MAP.get(currency, "$")
                },
                'user': {
                    'id': employee_id,
                    'email': user_email,
                    'authentication_type': authentication_type
                },
                'users_count': employees_count,
                'title': "New user joined organization"
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], subject, template_type="new_employee",
            template_params=template_params, reply_to_email=user_email)

    def get_authorized_employees(self, organization_id, **kwargs):
        employees = self._list(organization_id)
        auth_user_ids = list(map(lambda x: x.auth_user_id, employees))
        try:
            authorized_users = self._authorize_user_list(
                users=auth_user_ids, **kwargs)
        except requests.exceptions.HTTPError as ex:
            raise WrongArgumentsException(Err.OE0435, [str(ex)])
        return list(filter(
            lambda x: x.auth_user_id in authorized_users, employees))

    def _authorize_user_list(self, permissions, object_type, object_id, users):
        code, response = self.auth_client.authorize_user_list(
            users=users, actions=permissions,
            scope_type=object_type, scope_id=object_id)
        authorized_users = []
        if code == 200:
            for user_id in users:
                if all(map(lambda x: x in response[user_id], permissions)):
                    authorized_users.append(user_id)
        return authorized_users


class EmployeeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return EmployeeController
