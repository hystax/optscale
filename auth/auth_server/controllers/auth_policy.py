import logging

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from auth.auth_server.controllers.base import BaseController
from auth.auth_server.controllers.base_async import BaseAsyncControllerWrapper
from auth.auth_server.exceptions import Err
from auth.auth_server.models.models import (
    Assignment, AuthPolicy, AuthPolicyPurpose, AuthPolicyScope, Type)
from auth.auth_server.utils import check_kwargs_is_empty
from tools.optscale_exceptions.common_exc import (
    ConflictException, NotFoundException, WrongArgumentsException)
from tools.optscale_time import utcnow_timestamp

LOG = logging.getLogger(__name__)

ORGANIZATION_TYPE = 'organization'
# any role on the organization (member, engineer, manager)
READ_POLICY_ACTION = 'INFO_ORGANIZATION'
# carried by the organization manager role only
MANAGE_POLICY_ACTION = 'EDIT_PARTNER'
# only organization scope is managed until SSO introduces domain policies
SUPPORTED_SCOPE_TYPES = [AuthPolicyScope.organization.value]


class AuthPolicyController(BaseController):
    def _get_model_type(self):
        return AuthPolicy

    @staticmethod
    def _check_string(name, value):
        if value is None:
            raise WrongArgumentsException(Err.OA0032, [name])
        if not isinstance(value, str):
            raise WrongArgumentsException(Err.OA0033, [name])
        if not value or value.isspace():
            raise WrongArgumentsException(Err.OA0032, [name])

    def _check_scope(self, scope_type, scope_id):
        self._check_string('scope_type', scope_type)
        self._check_string('scope_id', scope_id)
        if scope_type not in SUPPORTED_SCOPE_TYPES:
            raise WrongArgumentsException(Err.OA0060, ['scope_type'])

    def _check_purpose(self, purpose):
        self._check_string('purpose', purpose)
        if purpose not in [p.value for p in AuthPolicyPurpose]:
            raise WrongArgumentsException(Err.OA0060, ['purpose'])

    def _check_organization_exists(self, organization_id):
        payload = ((ORGANIZATION_TYPE, organization_id),)
        if organization_id not in self.get_resources_info(payload):
            raise NotFoundException(
                Err.OA0028, [ORGANIZATION_TYPE, organization_id])

    def _check_access(self, token, scope_id, action):
        if token:
            self.check_permissions(token, ORGANIZATION_TYPE, scope_id, action)

    def _get_active_policies(self, scope_type, scope_id, purpose=None):
        query = self.session.query(AuthPolicy).filter(
            AuthPolicy.scope_type == AuthPolicyScope(scope_type),
            AuthPolicy.scope_id == scope_id,
            AuthPolicy.deleted.is_(False),
        )
        if purpose is not None:
            query = query.filter(
                AuthPolicy.purpose == AuthPolicyPurpose(purpose))
        return query.all()

    def list(self, scope_type=None, scope_id=None, token=None, **kwargs):
        check_kwargs_is_empty(**kwargs)
        self._check_scope(scope_type, scope_id)
        self._check_access(token, scope_id, READ_POLICY_ACTION)
        return self._get_active_policies(scope_type, scope_id)

    def create(self, token=None, **kwargs):
        scope_type = kwargs.pop('scope_type', None)
        scope_id = kwargs.pop('scope_id', None)
        purpose = kwargs.pop('purpose', None)
        check_kwargs_is_empty(**kwargs)
        self._check_scope(scope_type, scope_id)
        self._check_purpose(purpose)
        self._check_access(token, scope_id, MANAGE_POLICY_ACTION)
        self._check_organization_exists(scope_id)
        if self._get_active_policies(scope_type, scope_id, purpose):
            raise ConflictException(Err.OA0081, [])
        policy = AuthPolicy(
            scope_type=AuthPolicyScope(scope_type), scope_id=scope_id,
            purpose=AuthPolicyPurpose(purpose))
        self.session.add(policy)
        try:
            self.session.commit()
        except IntegrityError:
            # concurrent create of the same active policy
            self.session.rollback()
            raise ConflictException(Err.OA0081, [])
        LOG.info('Auth policy %s (%s) created for %s %s', policy.id,
                 purpose, scope_type, scope_id)
        return policy

    def delete(self, item_id, token=None, **kwargs):
        policy = self.get(item_id)
        if policy is None:
            raise NotFoundException(
                Err.OA0003, [AuthPolicy.__name__, item_id])
        self._check_access(token, policy.scope_id, MANAGE_POLICY_ACTION)
        policy.deleted_at = utcnow_timestamp()
        self.session.add(policy)
        self.session.commit()
        LOG.info('Auth policy %s (%s) deleted for %s %s', policy.id,
                 policy.purpose.value, policy.scope_type.value,
                 policy.scope_id)

    def get_user_organizations(self, user_id):
        rows = self.session.query(Assignment.resource_id).join(
            Type, and_(
                Type.id == Assignment.type_id,
                Type.name == ORGANIZATION_TYPE,
            )
        ).filter(
            Assignment.user_id == user_id,
            Assignment.deleted.is_(False),
            Assignment.resource_id.isnot(None),
        ).distinct().all()
        return [row[0] for row in rows]

    def get_enforcing_organizations(self, user_id):
        organization_ids = self.get_user_organizations(user_id)
        if not organization_ids:
            return []
        rows = self.session.query(AuthPolicy.scope_id).filter(
            AuthPolicy.scope_type == AuthPolicyScope.organization,
            AuthPolicy.purpose == AuthPolicyPurpose.mfa,
            AuthPolicy.scope_id.in_(organization_ids),
            AuthPolicy.deleted.is_(False),
        ).distinct().all()
        return sorted(row[0] for row in rows)

    def is_mfa_enforced_for_user(self, user_id):
        return bool(self.get_enforcing_organizations(user_id))


class AuthPolicyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AuthPolicyController
