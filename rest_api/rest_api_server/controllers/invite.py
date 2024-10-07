import datetime
import json
import logging
import requests
import uuid

from etcd import EtcdKeyNotFound

from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.employee import EmployeeController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import InviteAssignmentScopeTypes
from rest_api.rest_api_server.models.models import (
    Invite, InviteAssignment, Organization, Pool)
from rest_api.rest_api_server.utils import query_url

from optscale_client.herald_client.client_v2 import Client as HeraldClient

from tools.optscale_exceptions.common_exc import (
    NotFoundException, HeraldException, WrongArgumentsException)
from currency_symbols.currency_symbols import CURRENCY_SYMBOLS_MAP

LOG = logging.getLogger(__name__)


class InviteController(BaseController):
    def _get_model_type(self):
        return Invite

    @staticmethod
    def _validate_parameters(**params):
        pass

    def get_scopes(self, ids):
        scopes_map = {}
        organizations = self.session.query(
            Organization
        ).filter(
            Organization.deleted.is_(False),
            Organization.id.in_(ids)
        ).all()
        scopes_map.update(
            {org.id: org for org in organizations}
        )
        pools = self.session.query(
            Pool
        ).filter(
            Pool.deleted.is_(False),
            Pool.id.in_(ids)
        )
        scopes_map.update(
            {pool.id: pool for pool in pools}
        )
        return scopes_map

    def get_invite_expiration_days(self):
        try:
            invite_expiration_days = int(self._config.read('/restapi/invite_expiration_days').value)
        except EtcdKeyNotFound:
            invite_expiration_days = 30
        return invite_expiration_days

    def create(self, email, user_id, user_info, invite_assignments: 'list',
               show_link=False):
        def get_highest_role(current, new):
            roles_order_map = {
                'optscale_member': 0,
                'optscale_engineer': 1,
                'optscale_manager': 2,
            }
            if roles_order_map.get(current, 0) > roles_order_map.get(new, 0):
                return cur_role
            else:
                return new

        # TODO add check for one org per invite
        organization = None
        scopes_map = self.get_scopes(list(
            map(lambda x: x['scope_id'], invite_assignments)))
        scope_names = {}
        for scope_id, scope in scopes_map.items():
            org = self._get_org_by_scope(scope)
            scope_names[scope_id] = scope.name
            if not organization:
                organization = org
            if org.id not in scopes_map and org.id not in scope_names:
                scope_names[org.id] = org.name
                invite_assignments.append({
                    'scope_id': org.id,
                    'scope_type': InviteAssignmentScopeTypes.ORGANIZATION.value
                })
        scope_name_role_map = {}
        invite_id = str(uuid.uuid4())
        for assignment_info in invite_assignments:
            scope_entity_map = {
                'pool': Pool,
                'organization': Organization
            }
            if assignment_info['scope_id'] not in scope_names:
                raise WrongArgumentsException(
                    Err.OE0005,
                    [scope_entity_map[assignment_info['scope_type']].__name__,
                     assignment_info['scope_id']])
            invite_assignment = InviteAssignment(
                invite_id=invite_id,
                **assignment_info
            )
            self.session.add(invite_assignment)
            scope_name = scope_names.get(assignment_info['scope_id'])
            cur_role = scope_name_role_map.get(scope_name)
            new_role = assignment_info.get('purpose')
            scope_name_role_map[scope_name] = get_highest_role(
                cur_role, new_role) or 'optscale_member'
        meta = {
            'owner': {
                'name': user_info.get('display_name'),
                'email': user_info.get('email')
            },
            'scope_names': {k: v for k, v in scope_names.items()},
            'organization': organization.name,
            'organization_id': organization.id
        }
        invite_expiration_days = self.get_invite_expiration_days()

        invite = super().create(id=invite_id, email=email,
                                owner_id=user_id,
                                meta=json.dumps(meta),
                                ttl=int(
                                    datetime.datetime.utcnow().timestamp() +
                                    datetime.timedelta(
                                        days=invite_expiration_days
                                    ).total_seconds()))
        invite_dict = invite.to_dict()
        invite_url = self.generate_link(email)
        if show_link:
            invite_dict['url'] = invite_url
        self.send_notification(
            email, invite_url, organization.name, organization.id, organization.currency)
        meta = {
            'object_name': organization.name,
            'email': email,
            'scope_purposes': ', '.join('%s: %s' % (k, v)
                                        for k, v in scope_name_role_map.items())
        }

        self.publish_activities_task(
            organization.id, organization.id, 'organization',
            'employee_invited', meta, 'organization.employee_invited',
            add_token=True)
        return invite_dict

    def accept_invite(self, invite_id, user_info):
        invite = self.get_invite_for_user_info(invite_id, user_info)
        self._apply_invite(invite, user_info)

    def get_invite_for_user_info(self, invite_id, user_info):
        email = user_info['email']
        invite = self._get_invite_for_email(invite_id, email)
        return invite

    def _create_employees(self, organizations, user_info):
        employee_controller = EmployeeController(self.session, self._config)
        for org in organizations:
            employee_exists = employee_controller.is_employee_exists(
                org.id, auth_user_id=user_info['id'])
            if not employee_exists:
                employee = employee_controller.create(
                    organization_id=org.id,
                    name=user_info['display_name'],
                    auth_user_id=user_info['id'])
                employee_controller.send_new_employee_email(
                    org.id, org.name, org.currency, employee.id,
                    user_info['email'], user_info['is_password_autogenerated'])

    def _apply_invite(self, invite, user_info):
        scope_ids = [invite_assignment.scope_id
                     for invite_assignment in invite.invite_assignments]
        scopes_map = self.get_scopes(scope_ids)
        organizations = []
        for invite_assignment in invite.invite_assignments:
            self.assign_role_to_user(
                user_info['id'], invite_assignment.scope_id,
                invite_assignment.purpose.value,
                invite_assignment.scope_type.value)
            target_scope = scopes_map.get(invite_assignment.scope_id)
            if isinstance(target_scope, Organization
                          ) and target_scope not in organizations:
                organizations.append(target_scope)
        self._create_employees(organizations, user_info)
        self.delete_invite(invite)

    def decline_invite(self, invite_id, user_info):
        invite = self.get_invite_for_user_info(invite_id, user_info)
        self.delete_invite(invite)

    def delete_invite(self, invite):
        for invite_assignment in invite.invite_assignments:
            invite_assignment.deleted_at = int(datetime.datetime.utcnow().timestamp())
        super().delete(invite.id)

    def list(self, user_id, user_info):
        invites = super().list(email=user_info['email'])
        now = int(datetime.datetime.utcnow().timestamp())
        result = []
        for invite in invites:
            if invite.ttl <= now:
                invite.deleted_at = now
                continue
            result.append(invite)
        if len(invites) != len(result):
            self.session.commit()
        return result

    @staticmethod
    def _get_org_by_scope(scope):
        if isinstance(scope, Organization):
            return scope
        elif isinstance(scope, Pool):
            return scope.organization
        else:
            return None

    def _get_invite_for_email(self, invite_id, email):
        invite = super().get(item_id=invite_id, email=email)
        now = int(datetime.datetime.utcnow().timestamp())
        if not invite or invite.ttl <= now:
            if invite:
                self.update(invite_id, deleted_at=now)
            raise NotFoundException(Err.OE0002, [Invite.__name__, invite_id])
        return invite

    def check_user_exists(self, email):
        _, response = self.auth_client.user_exists(email, user_info=True)
        return response['exists'], response.get('user_info', {})

    def get_user_auth_assignments(self):
        self.auth_client.token = self.token
        _, resp = self.auth_client.my_assignment_list()
        return resp

    def check_user_is_org_manager(self, org_ids, pool_ids):
        if len(pool_ids) > 0:
            pools = self.session.query(Pool).filter(
                Pool.deleted.is_(False),
                Pool.id.in_(pool_ids))
            for pool in pools:
                org_ids.append(pool.organization_id)
        org_ids = set(org_ids)

        db_orgs = self.session.query(Organization).filter(
            Organization.deleted.is_(False),
            Organization.id.in_(org_ids))
        db_org_ids = set(x.id for x in db_orgs)
        if len(org_ids) != len(db_org_ids):
            org_not_exists = [org for org in org_ids if org not in db_org_ids]
            raise NotFoundException(Err.OE0002, [
                Organization.__name__, org_not_exists])

        resp = self.get_user_auth_assignments()
        orgs_count = 0
        for assignment in resp:
            if (assignment['assignment_resource'] in org_ids and
                    assignment['role_name'] == 'Manager'):
                orgs_count += 1
        return len(org_ids) == orgs_count

    def generate_link(self, email):
        try:
            host = self._config.public_ip()
        except EtcdKeyNotFound:
            LOG.error('Could not get ETCD public_ip for creation base_url')
            raise
        base_url = 'https://%s' % host
        params = '{base_params}'.format(
            base_params=query_url(email=email)
        )
        url = '{base_url}/{action}{params}'.format(
            base_url=base_url, action='invited', params=params)
        return url

    def send_notification(self, email, url, organization_name, organization_id, currency):
        subject = 'OptScale invitation notification'
        template_params = {
            'texts': {
                'organization': {
                    'id': organization_id,
                    'name': organization_name,
                    'currency_code': CURRENCY_SYMBOLS_MAP.get(currency, '$')
                },
            },
            'links': {
                'login_button': url
            }
        }
        template_type = "invite"
        try:
            HeraldClient(
                url=self._config.herald_url(),
                secret=self._config.cluster_secret()
            ).email_send(
                [email], subject, template_type=template_type,
                template_params=template_params
            )
        except requests.exceptions.HTTPError as exc:
            raise HeraldException(Err.OE0435, [str(exc)])


class InviteAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return InviteController
