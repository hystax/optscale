import json
from sqlalchemy import Enum, and_
from sqlalchemy import inspect
from sqlalchemy.ext.declarative.base import _declarative_constructor
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (Column, Integer, String, Boolean, Time, Table,
                        ForeignKey, UniqueConstraint, CheckConstraint)
from sqlalchemy.sql.expression import false
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from tools.cloud_adapter.cloud import SUPPORTED_BILLING_TYPES
from tools.cloud_adapter.model import ResourceTypes
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import (
    ModelEncoder, gen_id, now_timestamp, encode_string, decode_config,
    decrypt_bi_meta)
from rest_api.rest_api_server.models.enums import (
    CloudTypes, ImportStates, RolePurposes,
    AssignmentRequestStatuses, ThresholdBasedTypes, ThresholdTypes,
    ConstraintTypes, PoolPurposes, ConstraintLimitStates,
    OrganizationConstraintTypes, BIOrganizationStatuses, BITypes,
    GeminiStatuses)
from rest_api.rest_api_server.models.types import (
    Email, Name, Uuid, NullableUuid, NullableMetadata, Int,
    NullableString, AutogenUuid, NullableBool, NullableText, NullableInt,
    BaseString, BigInt, CloudType, RolePurpose,
    ImportState, AssignmentRequestStatus,
    ThresholdBasedType, ThresholdType, NotWhiteSpaceString,
    ConditionType, ConstraintType, PoolPurpose, BaseText,
    InviteAssignmentScopeType, NullableJSON, CachedResourceType, NullableFloat,
    CostModelType, WebhookObjectType, WebhookActionType,
    MediumNullableString, MediumString, MediumLargeNullableString,
    ConstraintLimitState, OrganizationConstraintType, ConstraintDefinition,
    RunResult, BIOrganizationStatus, BIType, Float, GeminiStatus,
    HMTimeString, TimezoneString)


class PermissionKeys(Enum):
    is_creatable = 'is_creatable'
    is_updatable = 'is_updatable'


class ColumnPermissions(Enum):
    full = {PermissionKeys.is_creatable: True,
            PermissionKeys.is_updatable: True}
    create_only = {PermissionKeys.is_creatable: True,
                   PermissionKeys.is_updatable: False}
    update_only = {PermissionKeys.is_creatable: False,
                   PermissionKeys.is_updatable: True}
    none = {PermissionKeys.is_creatable: False,
            PermissionKeys.is_updatable: False}


class Base(object):
    __table__: Table
    __name__: str

    def __init__(self, **kwargs):
        init_columns = list(filter(lambda x: x.info.get(
            PermissionKeys.is_creatable) is True, self.__table__.c))
        for col in init_columns:
            setattr(self, col.name, kwargs.get(col.name))
            kwargs.pop(col.name, None)
        _declarative_constructor(self, **kwargs)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


Base = declarative_base(cls=Base, constructor=None)


class BaseMixin(object):
    @hybrid_property
    def unique_fields(self):
        return list()

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


class BaseDeletableMixin(BaseMixin):
    deleted_at = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def deleted(self):
        return self.deleted_at != 0

    @hybrid_method
    def get_uniqueness_filter(self, is_new=True):
        inner_filter = [getattr(self.__table__.columns, x) == getattr(self, x)
                        for x in self.unique_fields
                        if getattr(self, x) is not None]
        outer_filter = [
            self.__class__.deleted.is_(False),
            and_(*inner_filter)
        ]

        if not is_new:
            outer_filter.append(self.__table__.columns.id != self.id)
        return outer_filter


class MutableMixin(BaseDeletableMixin):
    id = Column(NullableUuid('id'), primary_key=True, default=gen_id,
                info=ColumnPermissions.create_only)


class ImmutableMixin(BaseDeletableMixin):
    id = Column(NullableUuid('id'), primary_key=True, default=gen_id)


class ImmutableRequiredMixin(BaseDeletableMixin):
    id = Column(NullableUuid('id'), primary_key=True,
                info=ColumnPermissions.create_only)


class MetaMixin(object):
    meta = Column(NullableMetadata('meta'), info=ColumnPermissions.full)


class StateMixin(object):
    state = Column(String(256), default='new',
                   info=ColumnPermissions.update_only)


class DefaultMixin(object):
    default = Column(Boolean, default=True)


class ValidatorMixin(object):
    def get_validator(self, key, *args, **kwargs):
        return getattr(type(self), key).type.validator(*args, **kwargs)


class CreatedMixin(BaseDeletableMixin):
    created_at = Column(Integer, default=now_timestamp, nullable=False)


class Organization(Base, MutableMixin, ValidatorMixin, CreatedMixin):
    __tablename__ = 'organization'

    id = Column(AutogenUuid('id'), primary_key=True, default=gen_id,
                info=ColumnPermissions.create_only)
    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    # pool_id is nullable due to bidirectional relations with org and pool.
    # mysql doesn't support deferrable constraints, so it's the only way to
    # resolve an issue
    pool_id = Column(NullableUuid, ForeignKey('pool.id'),
                     nullable=True, info=ColumnPermissions.create_only)
    pool = relationship("Pool", foreign_keys=[pool_id])
    is_demo = Column(NullableBool('is_demo'), nullable=False, default=False,
                     info=ColumnPermissions.create_only)
    currency = Column(NotWhiteSpaceString('currency'), nullable=False,
                      info=ColumnPermissions.full, default='USD')
    cleaned_at = Column(NullableInt('cleaned_at'), default=0, nullable=False,
                        info=ColumnPermissions.update_only)

    @validates('id')
    def _validate_id(self, key, id):
        return self.get_validator(key, id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('currency')
    def _validate_currency(self, key, currency):
        return self.get_validator(key, currency, max_length=3)

    @validates('is_demo')
    def _validate_is_demo(self, key, name):
        return self.get_validator(key, name)

    @validates('cleaned_at')
    def _validate_cleaned_at(self, key, name):
        return self.get_validator(key, name)


class Pool(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'pool'

    limit = Column(BigInt('limit'), nullable=False, default=0,
                   info=ColumnPermissions.full)
    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'), nullable=False,
                             info=ColumnPermissions.create_only)
    organization = relationship('Organization', foreign_keys=[organization_id])
    parent_id = Column(NullableUuid('parent_id'), ForeignKey('pool.id'),
                       info=ColumnPermissions.create_only)
    children = relationship('Pool')
    purpose = Column(PoolPurpose, default=PoolPurposes.BUDGET,
                     info=ColumnPermissions.full, nullable=False)
    default_owner_id = Column(NullableUuid('default_owner_id'),
                              ForeignKey('employee.id'),
                              info=ColumnPermissions.full)
    default_owner = relationship("Employee", foreign_keys=[default_owner_id])
    __table_args__ = (UniqueConstraint(
        "name", "deleted_at", 'parent_id', 'organization_id',
        name="uc_name_del_at_parent_id_organization_id"),)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('id'):
            self.id = gen_id()

    def to_dict(self):
        pool_dict = super().to_dict()
        if self.default_owner:
            pool_dict['default_owner_name'] = self.default_owner.name
        else:
            pool_dict['default_owner_name'] = None

        total_children_limit = 0
        for child_pool in self.children:
            if child_pool.deleted_at == 0:
                total_children_limit += child_pool.limit
        pool_dict['unallocated_limit'] = self.limit - total_children_limit
        return pool_dict

    @hybrid_property
    def unique_fields(self):
        return ['name', 'parent_id', 'organization_id']

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('parent_id')
    def _validate_parent_id(self, key, parent_id):
        return self.get_validator(key, parent_id)

    @validates('purpose')
    def _validate_purpose(self, key, purpose):
        return self.get_validator(key, purpose)

    @validates('limit')
    def _validate_limit(self, key, limit):
        return self.get_validator(key, limit)


class CloudAccount(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    type = Column(CloudType, default=CloudTypes.AWS_CNR,
                  info=ColumnPermissions.create_only, nullable=False)
    config = Column(NullableText('config'), nullable=False,
                    info=ColumnPermissions.full)
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False,
                             info=ColumnPermissions.create_only)
    organization = relationship("Organization", backref='cloudaccount')
    cost_model_id = Column(Uuid('cost_model_id'), ForeignKey('cost_model.id'),
                           nullable=True, info=ColumnPermissions.create_only)
    cost_model = relationship('CostModel')
    auto_import = Column(NullableBool('auto_import'), nullable=False,
                         default=True, info=ColumnPermissions.full)
    import_period = Column(NullableInt('import_period'), default=1,
                           nullable=False, info=ColumnPermissions.none)
    last_import_at = Column(NullableInt('last_import_at'), default=0,
                            nullable=False, info=ColumnPermissions.update_only)
    last_import_modified_at = Column(NullableInt('last_import_modified_at'),
                                     default=0, nullable=False,
                                     info=ColumnPermissions.update_only)
    account_id = Column(NullableString('account_id'), nullable=True,
                        info=ColumnPermissions.none)
    process_recommendations = Column(
        NullableBool('process_recommendations'), nullable=False,
        default=True, info=ColumnPermissions.full)
    last_import_attempt_at = Column(
        NullableInt('last_import_attempt_at'), default=0, nullable=False,
        info=ColumnPermissions.update_only)
    last_import_attempt_error = Column(
        NullableText('last_import_attempt_error'),
        nullable=True, info=ColumnPermissions.update_only)
    last_getting_metrics_at = Column(
        NullableInt('last_getting_metrics_at'), default=0,
        nullable=False, info=ColumnPermissions.update_only)
    last_getting_metric_attempt_at = Column(
        NullableInt('last_getting_metric_attempt_at'), default=0, nullable=False,
        info=ColumnPermissions.update_only)
    last_getting_metric_attempt_error = Column(
        NullableText('last_getting_metric_attempt_error'),
        nullable=True, info=ColumnPermissions.update_only)
    cleaned_at = Column(NullableInt('cleaned_at'), default=0, nullable=False,
                        info=ColumnPermissions.update_only)
    parent_id = Column(
        NullableUuid('parent_id'), ForeignKey('cloudaccount.id'),
        nullable=True, info=ColumnPermissions.create_only)
    parent = relationship("CloudAccount", remote_side='CloudAccount.id')

    __table_args__ = (
        UniqueConstraint("organization_id", "name", "deleted_at",
                         name="uc_org_name_del_at"),
        UniqueConstraint("account_id", "type", 'organization_id',
                         'deleted_at', name="uc_account_type_org_id_del_at"),)

    @validates('name', 'type', 'organization_id', 'config', 'auto_import',
               'import_period', 'last_import_at', 'account_id', 'parent_id',
               'last_import_modified_at', 'process_recommendations')
    def _validate_params(self, key, param):
        return self.get_validator(key, param)

    @hybrid_property
    def unique_fields(self):
        return ['name', 'organization_id']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('id'):
            self.id = gen_id()

    @hybrid_property
    def decoded_config(self):
        return decode_config(self.config)

    def to_dict(self, secure=False):
        cloud_acc_dict = super().to_dict()
        cloud_acc_dict['type'] = cloud_acc_dict['type'].value
        if self.parent_id and self.parent and self.parent.deleted_at == 0:
            config = self.parent.decoded_config
            config.update(self.decoded_config)
        else:
            config = self.decoded_config
        if cloud_acc_dict.pop('cost_model_id', None):
            config['cost_model'] = self.cost_model.loaded_value
        if secure:
            adapter_cls = SUPPORTED_BILLING_TYPES.get(cloud_acc_dict['type'])
            for p in adapter_cls.BILLING_CREDS:
                if p.protected:
                    config.pop(p.name, None)
        cloud_acc_dict['config'] = config
        return cloud_acc_dict

    def to_json(self):
        return json.dumps(self.to_dict(secure=True), cls=ModelEncoder)


class CostModel(Base, CreatedMixin, ImmutableRequiredMixin, ValidatorMixin):
    __tablename__ = 'cost_model'

    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False,
                             info=ColumnPermissions.create_only)
    type = Column(CostModelType, nullable=False,
                  info=ColumnPermissions.create_only)
    value = Column(NullableJSON('value'),
                   info=ColumnPermissions.full, nullable=False)

    @hybrid_property
    def loaded_value(self):
        return json.loads(self.value)

    @validates('type')
    def _validate_type(self, key, type_):
        return self.get_validator(key, type_)

    @validates('value')
    def _validate_value(self, key, value):
        return self.get_validator(key, value)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    def to_dict(self):
        res = super().to_dict()
        res['value'] = json.loads(res.pop('value'))
        return res


class K8sNode(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'k8s_node'

    cloud_account_id = Column(
        Uuid('cloud_account_id'), ForeignKey('cloudaccount.id'),
        nullable=False, info=ColumnPermissions.full)
    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    last_seen = Column(Int('last_seen'), nullable=False,
                       info=ColumnPermissions.full)
    flavor = Column(NullableString('flavor'), nullable=True,
                    info=ColumnPermissions.full)
    cpu = Column(Int('cpu'), nullable=False,
                 info=ColumnPermissions.full)
    memory = Column(Int('memory'), nullable=False,
                    info=ColumnPermissions.full)
    provider_id = Column(NullableString('provider_id'), nullable=True,
                         info=ColumnPermissions.full)
    hourly_price = Column(NullableFloat('hourly_price'), nullable=True,
                          info=ColumnPermissions.full)

    __table_args__ = (UniqueConstraint(
        'cloud_account_id', 'name', 'provider_id', 'deleted_at',
        name="uc_cloud_acc_id_name_provider_id_deleted_at"),)

    @hybrid_property
    def provider(self):
        if not self.provider_id:
            return None
        clean_provider = next(iter(self.provider_id.split(':///')), None)
        return clean_provider + '_cnr' if clean_provider else None

    @validates('cloud_account_id')
    def _validate_cloud_account_id(self, key, cloud_account_id):
        return self.get_validator(key, cloud_account_id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('flavor')
    def _validate_cloud_flavor(self, key, flavor):
        return self.get_validator(key, flavor)

    @validates('provider_id')
    def _validate_provider_id(self, key, provider_id):
        return self.get_validator(key, provider_id)

    @validates('last_seen')
    def _validate_last_seen(self, key, last_seen):
        return self.get_validator(key, last_seen)

    @validates('hourly_price')
    def _validate_hourly_price(self, key, hourly_price):
        return self.get_validator(key, hourly_price)

    @validates('cpu')
    def _validate_cpu(self, key, cpu):
        return self.get_validator(key, cpu)

    @validates('memory')
    def _validate_memory(self, key, memory):
        return self.get_validator(key, memory)

    def to_dict(self):
        result = super().to_dict()
        result['provider'] = self.provider
        return result

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('id'):
            self.id = gen_id()


class DiscoveryInfo(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'discovery_info'

    cloud_account_id = Column(
        Uuid('cloud_account_id'), ForeignKey('cloudaccount.id'),
        nullable=False, info=ColumnPermissions.create_only)
    resource_type = Column(
        CachedResourceType, nullable=False,
        info=ColumnPermissions.create_only)
    observe_time = Column(
        NullableInt('observe_time'), default=0, nullable=False,
        info=ColumnPermissions.update_only)
    last_discovery_at = Column(
        NullableInt('last_discovery_at'), default=0, nullable=False,
        info=ColumnPermissions.update_only)
    last_error_at = Column(
        NullableInt('last_error_at'), default=0, nullable=False,
        info=ColumnPermissions.update_only)
    last_error = Column(
        NullableText('last_error'),
        nullable=True, info=ColumnPermissions.update_only)
    enabled = Column(NullableBool('enable'), nullable=False, default=True,
                     info=ColumnPermissions.full)

    __table_args__ = (UniqueConstraint(
        'cloud_account_id', 'resource_type', 'deleted_at',
        name="uc_cloud_acc_id_del_at"),)

    @validates('cloud_account_id')
    def _validate_cloud_account_id(self, key, cloud_account_id):
        return self.get_validator(key, cloud_account_id)

    @validates('resource_type')
    def _validate_resource_type(self, key, resource_type):
        return self.get_validator(key, resource_type)

    @validates('observe_time')
    def _validate_observe_time(self, key, observe_time):
        return self.get_validator(key, observe_time)

    @validates('last_discovery_at')
    def _validate_last_discovery_at(self, key, last_discovery_at):
        return self.get_validator(key, last_discovery_at)

    @validates('last_error_at')
    def _validate_last_error_at(self, key, last_error_at):
        return self.get_validator(key, last_error_at)

    @validates('last_error')
    def _validate_last_error(self, key, last_error):
        return self.get_validator(key, last_error)

    @validates('enabled')
    def _validate_enabled(self, key, enabled):
        return self.get_validator(key, enabled)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'resource_type': ResourceTypes(result['resource_type']).name
        })
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ModelEncoder)


class Employee(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    name = Column(Name, nullable=False, info=ColumnPermissions.full)
    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'),
        nullable=False, info=ColumnPermissions.create_only)
    organization = relationship('Organization')
    auth_user_id = Column(NullableUuid('auth_user_id'), nullable=True,
                          info=ColumnPermissions.create_only)

    __table_args__ = (UniqueConstraint(
        'organization_id', "auth_user_id", "deleted_at",
        name="uc_employee_org_auth_user"),)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'default_ssh_key_id':
                # pylint: disable=no-member
                self.default_ssh_key[0].id if self.default_ssh_key else None
        })
        return result

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)


class ReportImport(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    cloud_account_id = Column(
        Uuid('cloud_account_id'), ForeignKey('cloudaccount.id'),
        nullable=False, info=ColumnPermissions.create_only)
    cloud_account = relationship('CloudAccount')
    import_file = Column(NullableString('import_file'),
                         nullable=True, info=ColumnPermissions.create_only)
    state = Column(ImportState, default=ImportStates.SCHEDULED,
                   nullable=False, info=ColumnPermissions.full)
    state_reason = Column(NullableText('state_reason'),
                          nullable=True, info=ColumnPermissions.full)
    is_recalculation = Column(NullableBool('is_recalculation'), nullable=False,
                              default=False, info=ColumnPermissions.create_only)
    updated_at = Column(NullableInt('updated_at'), default=0, nullable=False,
                        info=ColumnPermissions.update_only)

    @validates('cloud_account_id')
    def _validate_cloud_account_id(self, key, cloud_account_id):
        return self.get_validator(key, cloud_account_id)

    @validates('import_file')
    def _validate_import_file(self, key, import_file):
        return self.get_validator(key, import_file)

    @validates('state')
    def _validate_state(self, key, state):
        return self.get_validator(key, state)

    @validates('state_reason')
    def _validate_state_reason(self, key, state_reason):
        return self.get_validator(key, state_reason)


class Invite(Base, CreatedMixin, MutableMixin, ValidatorMixin):
    email = Column(Email, info=ColumnPermissions.create_only, nullable=False)
    owner_id = Column(NullableUuid('owner_id'), nullable=False,
                      info=ColumnPermissions.create_only)
    ttl = Column(Integer, nullable=False, info=ColumnPermissions.create_only,
                 default=0)
    meta = Column(NullableMetadata('meta'), info=ColumnPermissions.create_only,
                  nullable=False, default='{}')

    def to_dict(self):
        result = super().to_dict()
        meta_str = result.pop('meta')
        meta = json.loads(meta_str)
        result['owner_name'] = meta.get('owner', {}).get('name')
        result['owner_email'] = meta.get('owner', {}).get('email')
        result['organization'] = meta.get('organization')
        result['organization_id'] = meta.get('organization_id')
        result['invite_assignments'] = []
        # pylint: disable=no-member
        for invite_assignment in self.invite_assignments:
            result['invite_assignments'].append({
                'id': invite_assignment.id,
                'scope_id': invite_assignment.scope_id,
                'scope_type': invite_assignment.scope_type,
                'purpose': invite_assignment.purpose.value,
                'scope_name': meta.get(
                    'scope_names', {}).get(
                    invite_assignment.scope_id)
            })
        return result

    def __repr__(self):
        return '<Invite %s>' % self.email

    @validates('email')
    def _validate_email(self, key, email):
        return self.get_validator(key, email)

    @validates('owner_id')
    def _validate_owner_id(self, key, owner_id):
        return self.get_validator(key, owner_id)

    @validates('meta')
    def _validate_meta(self, key, meta):
        return self.get_validator(key, meta)


class InviteAssignment(Base, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'invite_assignment'

    invite_id = Column(
        Uuid('invite_id'), ForeignKey('invite.id'),
        nullable=False, primary_key=True)
    scope_id = Column(Uuid('scope_id'), nullable=False, primary_key=True)
    scope_type = Column(InviteAssignmentScopeType,
                        nullable=False, info=ColumnPermissions.create_only)
    purpose = Column(RolePurpose, default=RolePurposes.optscale_member,
                     nullable=False, info=ColumnPermissions.full)
    invite = relationship(
        "Invite", backref="invite_assignments",
        primaryjoin="and_(InviteAssignment.invite_id==Invite.id, "
                    "InviteAssignment.deleted_at==0)")
    __table_args__ = (UniqueConstraint('invite_id', "scope_id",
                                       name="uc_invite_id_scope_id"),)

    @validates('invite_id')
    def _validate_invite_id(self, key, invite_id):
        return self.get_validator(key, invite_id)

    @validates('scope_id')
    def _validate_scope_id(self, key, scope_id):
        return self.get_validator(key, scope_id)

    @validates('scope_type')
    def _validate_scope_type(self, key, scope_type):
        return self.get_validator(key, scope_type)

    @validates('purpose')
    def _validate_purpose(self, key, purpose):
        return self.get_validator(key, purpose)

    def __repr__(self):
        return '<InviteAssignment %s %s: %s>' % (
            self.id, self.scope_id, self.purpose)

    def __init__(self, invite_id, scope_id, scope_type, purpose=None):
        self.invite_id = invite_id
        self.scope_id = scope_id
        self.scope_type = scope_type
        self.purpose = purpose


class AssignmentRequest(Base, CreatedMixin, ImmutableMixin):
    __tablename__ = 'assignment_request'

    resource_id = Column(Uuid('resource_id'), nullable=False,
                         info=ColumnPermissions.create_only, index=True)
    source_pool_id = Column(Uuid, ForeignKey('pool.id'), nullable=False,
                            info=ColumnPermissions.create_only)
    message = Column(NullableString('message'), info=ColumnPermissions.full,
                     nullable=True, default='')
    approver_id = Column(NullableUuid('approver_id'),
                         ForeignKey('employee.id'),
                         info=ColumnPermissions.create_only,
                         nullable=False)
    requester_id = Column(NullableUuid('requester_id'),
                          ForeignKey('employee.id'),
                          nullable=False,
                          info=ColumnPermissions.create_only)
    approver = relationship("Employee", foreign_keys=[approver_id])
    requester = relationship("Employee", foreign_keys=[requester_id])
    status = Column(AssignmentRequestStatus,
                    default=AssignmentRequestStatuses.PENDING,
                    nullable=False, info=ColumnPermissions.full)

    __table_args__ = (UniqueConstraint('resource_id', "deleted_at",
                                       name="uc_resource_id_deleted_at"),)


class PoolAlert(Base, CreatedMixin, MutableMixin, ValidatorMixin):
    __tablename__ = 'pool_alert'

    pool_id = Column(Uuid('pool_id'), ForeignKey('pool.id'),
                     nullable=False, info=ColumnPermissions.create_only)
    pool = relationship("Pool", foreign_keys=[pool_id])
    threshold = Column(Integer, nullable=False, info=ColumnPermissions.full)
    threshold_type = Column(ThresholdType, default=ThresholdTypes.ABSOLUTE,
                            nullable=False, info=ColumnPermissions.full)
    based = Column(ThresholdBasedType, default=ThresholdBasedTypes.COST,
                   nullable=False, info=ColumnPermissions.full)
    last_shoot_at = Column(Integer, default=0, nullable=False)
    include_children = Column(Boolean, info=ColumnPermissions.full,
                              default=False, nullable=False)

    @validates('threshold_type')
    def _validate_threshold_type(self, key, threshold_type):
        return self.get_validator(key, threshold_type)

    @validates('based')
    def _validate_based(self, key, based):
        return self.get_validator(key, based)

    @validates('pool_id')
    def _validate_pool_id(self, key, pool_id):
        return self.get_validator(key, pool_id)

    def to_dict(self):
        alert_dict = super().to_dict()
        alert_dict['contacts'] = []
        # pylint: disable=no-member
        for contact in self.contacts:
            alert_dict['contacts'].append(contact.to_dict())
        return alert_dict


class AlertContact(Base, BaseMixin):
    __tablename__ = 'alert_contact'

    id = Column(String(36), default=gen_id, primary_key=True, unique=True)
    pool_alert_id = Column(Uuid, ForeignKey('pool_alert.id'), nullable=False)
    pool_alert = relationship("PoolAlert", foreign_keys=[pool_alert_id],
                              backref="contacts")
    employee_id = Column(Uuid, ForeignKey('employee.id'), nullable=True)
    slack_channel_id = Column(Uuid, nullable=True)
    slack_team_id = Column(Uuid, nullable=True)

    def __init__(self, employee_id=None, pool_alert_id=None,
                 slack_channel_id=None, slack_team_id=None):
        self.id = gen_id()
        self.employee_id = employee_id
        self.pool_alert_id = pool_alert_id
        self.slack_channel_id = slack_channel_id
        self.slack_team_id = slack_team_id


class Rule(Base, CreatedMixin, ImmutableMixin):
    name = Column(Name, nullable=False, info=ColumnPermissions.full)
    priority = Column(Integer, nullable=False, info=ColumnPermissions.full)
    creator_id = Column(NullableUuid('creator_id'),
                        ForeignKey('employee.id'),
                        info=ColumnPermissions.create_only,
                        nullable=False)
    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'), nullable=False)
    organization = relationship('Organization')

    active = Column(Boolean, nullable=False,
                    default=True,
                    info=ColumnPermissions.full)
    pool_id = Column(Uuid, ForeignKey('pool.id'), nullable=False,
                     info=ColumnPermissions.full)
    pool = relationship("Pool", foreign_keys=[pool_id])
    owner_id = Column(Uuid('owner_id'), ForeignKey('employee.id'),
                      nullable=False,
                      info=ColumnPermissions.full)
    owner = relationship("Employee", foreign_keys=[owner_id])
    conditions = relationship("Condition")

    __table_args__ = (
        UniqueConstraint("name", "deleted_at", "organization_id",
                         name="uc_name_del_at_org_id"),
        UniqueConstraint("priority", "deleted_at", "organization_id",
                         name="uc_priority_del_at_org_id"),
    )

    def to_dict(self, raw=False):
        rule_dict = super().to_dict()
        if not raw:
            keys_to_delete = ['deleted_at']
            for key in keys_to_delete:
                rule_dict.pop(key)
            rule_dict['conditions'] = []
            for condition in self.conditions:
                if not condition.deleted:
                    rule_dict['conditions'].append(condition.to_dict())
        return rule_dict


class Condition(Base, CreatedMixin, ImmutableMixin):
    type = Column(ConditionType, nullable=False,
                  info=ColumnPermissions.create_only)
    rule_id = Column(Uuid('rule_id'), ForeignKey('rule.id'),
                     nullable=False,
                     info=ColumnPermissions.full)
    meta_info = Column(BaseString, nullable=False, info=ColumnPermissions.full)

    def to_dict(self, raw=False):
        cond_dict = super().to_dict()
        if not raw:
            keys_to_delete = ['created_at', 'deleted_at', 'rule_id']
            for key in keys_to_delete:
                cond_dict.pop(key)
        return cond_dict


class ResourceConstraint(Base, CreatedMixin, MutableMixin, ValidatorMixin):
    __tablename__ = 'resource_constraint'

    type = Column(ConstraintType('type'), default=ConstraintTypes.TTL,
                  nullable=False, info=ColumnPermissions.create_only)
    limit = Column(Int('limit'), default=0, nullable=False,
                   info=ColumnPermissions.full)
    resource_id = Column(Uuid('resource_id'), nullable=False,
                         info=ColumnPermissions.create_only, index=True)
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False, info=ColumnPermissions.create_only)
    __table_args__ = (UniqueConstraint(
        "type", "resource_id", "deleted_at", name="uc_name_del_at_parent_id"),)

    @validates('resource_id')
    def _validate_resource_id(self, key, resource_id):
        return self.get_validator(key, resource_id)

    @validates('type')
    def _validate_type(self, key, type):
        return self.get_validator(key, type)

    @validates('limit')
    def _validate_limit(self, key, limit):
        return self.get_validator(key, limit)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)


class PoolPolicy(Base, CreatedMixin, MutableMixin, ValidatorMixin):
    __tablename__ = 'pool_policy'

    type = Column(ConstraintType('type'), default=ConstraintTypes.TTL,
                  nullable=False, info=ColumnPermissions.create_only)
    limit = Column(Int('limit'), default=0, nullable=False,
                   info=ColumnPermissions.full)
    active = Column(NullableBool('active'), nullable=False, default=True,
                    info=ColumnPermissions.full)
    pool_id = Column(Uuid('pool_id'), ForeignKey('pool.id'),
                     nullable=False, info=ColumnPermissions.create_only)
    pool = relationship("Pool", backref="policies",
                        foreign_keys=[pool_id])
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False, info=ColumnPermissions.create_only)
    __table_args__ = (UniqueConstraint("type", "pool_id", "deleted_at",
                                       name="uc_name_del_at_parent_id"),)

    @validates('pool_id')
    def _validate_pool_id(self, key, pool_id):
        return self.get_validator(key, pool_id)

    @validates('type')
    def _validate_type(self, key, type):
        return self.get_validator(key, type)

    @validates('limit')
    def _validate_limit(self, key, limit):
        return self.get_validator(key, limit)

    @validates('active')
    def _validate_active(self, key, active):
        return self.get_validator(key, active)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)


class ConstraintLimitHit(Base, CreatedMixin, MutableMixin, ValidatorMixin):
    __tablename__ = 'constraint_limit_hit'

    resource_id = Column(Uuid('resource_id'), nullable=False,
                         info=ColumnPermissions.create_only, index=True)
    pool_id = Column(NullableUuid('pool_id'), ForeignKey('pool.id'),
                     nullable=True, info=ColumnPermissions.create_only)
    type = Column(ConstraintType('type'), default=ConstraintTypes.TTL,
                  nullable=False, info=ColumnPermissions.create_only)
    constraint_limit = Column(Int('constraint_limit'), nullable=False,
                              info=ColumnPermissions.create_only)
    ttl_value = Column(NullableInt('ttl_value'), nullable=True,
                       info=ColumnPermissions.create_only)
    expense_value = Column(NullableFloat('expense_value'), nullable=True,
                           info=ColumnPermissions.create_only)
    time = Column(NullableInt('time'), default=now_timestamp, nullable=False)
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False, info=ColumnPermissions.create_only)
    state = Column(ConstraintLimitState('state'),
                   default=ConstraintLimitStates.RED, nullable=False,
                   info=ColumnPermissions.none)

    __table_args__ = (CheckConstraint(
        '(ttl_value IS NULL) <> (expense_value IS NULL)', name='hit_value_xor'),)

    @validates('pool_id')
    def _validate_pool_id(self, key, pool_id):
        return self.get_validator(key, pool_id)

    @validates('resource_id')
    def _validate_resource_id(self, key, resource_id):
        return self.get_validator(key, resource_id)

    @validates('type')
    def _validate_type(self, key, type):
        return self.get_validator(key, type)

    @validates('constraint_limit')
    def _validate_constraint_limit(self, key, constraint_limit):
        return self.get_validator(key, constraint_limit)

    @validates('ttl_value')
    def _validate_ttl_value(self, key, ttl_value):
        return self.get_validator(key, ttl_value)

    @validates('expense_value')
    def _validate_expense_value(self, key, expense_value):
        return self.get_validator(key, expense_value)

    @validates('time')
    def _validate_time(self, key, time):
        return self.get_validator(key, time)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('state')
    def _validate_state(self, key, state):
        return self.get_validator(key, state)


class Checklist(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             info=ColumnPermissions.create_only,
                             nullable=False)
    organization = relationship("Organization", foreign_keys=[organization_id])
    last_run = Column(NullableInt('last_run'), default=0,
                      nullable=False, info=ColumnPermissions.full)
    next_run = Column(NullableInt('next_run'), default=now_timestamp,
                      nullable=False, info=ColumnPermissions.full)
    last_completed = Column(NullableInt('last_completed'), default=0,
                            nullable=False, info=ColumnPermissions.full)

    __table_args__ = (
        UniqueConstraint("deleted_at", "organization_id",
                         name="uc_del_at_org_id"),
    )

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('last_run')
    def _validate_last_run(self, key, last_run):
        return self.get_validator(key, last_run)

    @validates('next_run')
    def _validate_next_run(self, key, next_run):
        return self.get_validator(key, next_run)

    @validates('last_completed')
    def _validate_last_completed(self, key, last_completed):
        return self.get_validator(key, last_completed)


class OrganizationOption(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'organization_option'

    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             info=ColumnPermissions.create_only,
                             nullable=False)
    organization = relationship("Organization", foreign_keys=[organization_id])
    name = Column(NotWhiteSpaceString('name'), nullable=False, info=ColumnPermissions.create_only)
    value = Column(NullableMetadata('value'), info=ColumnPermissions.full,
                   nullable=False, default='{}')

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('value')
    def _validate_value(self, key, value):
        return self.get_validator(key, value)


class ClusterType(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'cluster_type'

    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'),
        info=ColumnPermissions.create_only, nullable=False)
    organization = relationship("Organization", foreign_keys=[organization_id])
    name = Column(Name, nullable=False, info=ColumnPermissions.create_only)
    tag_key = Column(BaseString, nullable=False,
                     info=ColumnPermissions.create_only)
    priority = Column(Int, nullable=False, info=ColumnPermissions.full)

    __table_args__ = (
        UniqueConstraint("name", "deleted_at", "organization_id",
                         name="uc_name_del_at_org_id"),
        UniqueConstraint("priority", "deleted_at", "organization_id",
                         name="uc_priority_del_at_org_id"),
    )

    @hybrid_property
    def encoded_tag_key(self):
        return encode_string(self.tag_key)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('tag_key')
    def _validate_tag_key(self, key, tag_key):
        return self.get_validator(key, tag_key)

    @validates('priority')
    def _validate_priority(self, key, priority):
        return self.get_validator(key, priority)


class PoolExpensesExport(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'expenses_export'

    pool_id = Column(NullableUuid('pool_id'), ForeignKey('pool.id'),
                     nullable=False, info=ColumnPermissions.create_only)
    pool = relationship("Pool", foreign_keys=[pool_id])

    __table_args__ = (
        UniqueConstraint("deleted_at", "pool_id", name="uc_pool_id_deleted_at"),
    )

    @validates('pool_id')
    def _validate_pool_id(self, key, pool_id):
        return self.get_validator(key, pool_id)


class ShareableBooking(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'shareable_booking'

    resource_id = Column(Uuid('resource_id'), nullable=False,
                         info=ColumnPermissions.create_only, index=True)
    acquired_by_id = Column(Uuid('acquired_by_id'),
                            ForeignKey('employee.id'),
                            nullable=False,
                            info=ColumnPermissions.create_only)
    acquired_by = relationship("Employee", foreign_keys=[acquired_by_id])
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'), nullable=False,
                             info=ColumnPermissions.create_only)
    organization = relationship("Organization", foreign_keys=[organization_id])
    acquired_since = Column(NullableInt('acquired_since'),
                            default=now_timestamp, nullable=False,
                            info=ColumnPermissions.full)
    released_at = Column(NullableInt('released_at'), default=0,
                         nullable=False, info=ColumnPermissions.full)
    ssh_key = Column(NullableJSON('ssh_key'), nullable=True,
                     info=ColumnPermissions.full)
    jira_auto_release = Column(NullableBool('jira_auto_release'),
                               info=ColumnPermissions.full,
                               default=False, nullable=False)
    event_id = Column(NullableString('event_id'), nullable=True,
                      info=ColumnPermissions.full)
    __table_args__ = (UniqueConstraint("organization_id", "event_id",
                                       name="uc_calendar_id_event_id"),)

    @hybrid_method
    def is_active(self, compared_ts):
        return self.acquired_since <= compared_ts and (
            self.released_at == 0 or compared_ts < self.released_at)

    @validates('resource_id')
    def _validate_resource_id(self, key, resource_id):
        return self.get_validator(key, resource_id)

    @validates('acquired_by_id')
    def _validate_acquired_by_id(self, key, acquired_by_id):
        return self.get_validator(key, acquired_by_id)

    @validates('acquired_since')
    def _validate_acquired_since(self, key, acquired_since):
        return self.get_validator(key, acquired_since)

    @validates('released_at')
    def _validate_released_at(self, key, released_at):
        return self.get_validator(key, released_at)

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('jira_auto_release')
    def _validate_jira_auto_release(self, key, jira_auto_release):
        return self.get_validator(key, jira_auto_release)

    def to_dict(self):
        result = super().to_dict()
        result['jira_issue_attachments'] = []
        # pylint: disable=no-member
        for jira_issue_attachment in self.jira_issue_attachments:
            result['jira_issue_attachments'].append(
                jira_issue_attachment.to_dict()
            )
        return result

    @validates('event_id')
    def _validate_event_id(self, key, event_id):
        return self.get_validator(key, event_id, max_length=40)


class CalendarSynchronization(Base, CreatedMixin, ImmutableMixin,
                              ValidatorMixin):
    __tablename__ = 'calendar_synchronization'

    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'),
        info=ColumnPermissions.create_only, nullable=False)
    calendar_id = Column(BaseString, nullable=False,
                         info=ColumnPermissions.create_only)
    last_completed = Column(NullableInt('last_completed'), default=0,
                            nullable=False, info=ColumnPermissions.full)

    __table_args__ = (
        UniqueConstraint("deleted_at", "organization_id",
                         name="uc_org_id_deleted_at"),
    )

    @hybrid_property
    def shareable_link(self):
        encoded_id = encode_string(self.calendar_id)
        return 'https://calendar.google.com/calendar/u/0?cid=%s' % encoded_id

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('calendar_id')
    def _validate_calendar_id(self, key, calendar_id):
        return self.get_validator(key, calendar_id)

    @validates('last_completed')
    def _validate_last_completed(self, key, last_completed):
        return self.get_validator(key, last_completed)

    @hybrid_property
    def unique_fields(self):
        return ['organization_id']

    def to_dict(self):
        res = super().to_dict()
        res['shareable_link'] = self.shareable_link
        return res


class Webhook(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'),
        nullable=False, info=ColumnPermissions.create_only)
    organization = relationship('Organization', foreign_keys=[organization_id])
    object_type = Column(WebhookObjectType, nullable=False,
                         info=ColumnPermissions.create_only)
    object_id = Column(Uuid('object_id'), nullable=False,
                       info=ColumnPermissions.create_only, index=True)
    active = Column(NullableBool('active'), nullable=False, default=True,
                    info=ColumnPermissions.full)
    action = Column(WebhookActionType, nullable=False,
                    info=ColumnPermissions.create_only)
    url = Column(NullableText('url'), nullable=False,
                 info=ColumnPermissions.full)
    headers = Column(NullableJSON('headers'), nullable=True,
                     info=ColumnPermissions.full)
    __table_args__ = (UniqueConstraint(
        "organization_id", "deleted_at", "object_id", "action",
        name="uc_org_id_deleted_at_obj_id_action"),
    )

    @hybrid_property
    def unique_fields(self):
        return ['action', 'object_id', 'organization_id']

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    @validates('object_type')
    def _validate_object_type(self, key, object_type):
        return self.get_validator(key, object_type)

    @validates('object_id')
    def _validate_object_id(self, key, object_id):
        return self.get_validator(key, object_id)

    @validates('active')
    def _validate_active(self, key, active):
        return self.get_validator(key, active)

    @validates('action')
    def _validate_action(self, key, action):
        return self.get_validator(key, action)

    @validates('url')
    def _validate_url(self, key, url):
        return self.get_validator(key, url)

    @validates('headers')
    def _validate_headers(self, key, headers):
        return self.get_validator(key, headers)


class SshKey(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'ssh_key'

    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    employee_id = Column(Uuid('employee_id'), ForeignKey('employee.id'),
                         nullable=False, info=ColumnPermissions.create_only)
    default = Column(NullableBool('default'), default=False, nullable=False,
                     info=ColumnPermissions.full)
    fingerprint = Column(NullableString('fingerprint'), nullable=False,
                         info=ColumnPermissions.create_only)
    key = Column(BaseText('key'), nullable=False,
                 info=ColumnPermissions.create_only)
    employee = relationship(
        "Employee", backref="default_ssh_key",
        primaryjoin="and_(SshKey.employee_id==Employee.id, "
                    "SshKey.deleted_at==0,"
                    "SshKey.default==1)")
    __table_args__ = (
        UniqueConstraint(
            "employee_id", "fingerprint", "deleted_at",
            name="uc_employee_id_fingerprint_deleted_at"),
    )

    @hybrid_property
    def unique_fields(self):
        return ['employee_id', 'fingerprint']

    @validates('name')
    def _validate_name(self, key, name):
        return self.get_validator(key, name)

    @validates('employee_id')
    def _validate_employee_id(self, key, employee_id):
        return self.get_validator(key, employee_id)

    @validates('default')
    def _validate_default(self, key, default):
        return self.get_validator(key, default)

    @validates('fingerprint')
    def _validate_fingerprint(self, key, fingerprint):
        return self.get_validator(key, fingerprint)

    @validates('key')
    def _validate_key(self, key, k):
        return self.get_validator(key, k)


class JiraIssueAttachment(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'jira_issue_attachment'

    client_key = Column(MediumLargeNullableString('client_key'),
                        nullable=False, info=ColumnPermissions.create_only)
    project_key = Column(BaseString('project_key'), nullable=False,
                         info=ColumnPermissions.create_only)
    issue_number = Column(Int('issue_number'), nullable=False,
                          info=ColumnPermissions.create_only)
    shareable_booking_id = Column(
        Uuid('shareable_booking_id'), ForeignKey('shareable_booking.id'),
        nullable=False, info=ColumnPermissions.create_only)
    shareable_booking = relationship("ShareableBooking",
                                     foreign_keys=[shareable_booking_id])
    status = Column(MediumString('status'), nullable=False,
                    info=ColumnPermissions.full)
    issue_link = Column(NullableText('issue_link'), nullable=False,
                        info=ColumnPermissions.create_only)
    auto_detach_status = Column(MediumNullableString('status'), nullable=True,
                                info=ColumnPermissions.full)
    shareable_bookings = relationship(
        "ShareableBooking", backref="jira_issue_attachments",
        primaryjoin="and_(JiraIssueAttachment.shareable_booking_id==ShareableBooking.id, "
                    "JiraIssueAttachment.deleted_at==0)")
    __table_args__ = (UniqueConstraint(
        'shareable_booking_id', 'client_key', 'project_key', 'issue_number',
        'deleted_at', name="uc_book_id_client_project_issue_deleted_at"),)

    @validates('client_key')
    def _validate_client_key(self, key, client_key):
        return self.get_validator(key, client_key)

    @validates('project_key')
    def _validate_project_key(self, key, project_key):
        return self.get_validator(key, project_key)

    @validates('issue_number')
    def _validate_issue_number(self, key, issue_number):
        return self.get_validator(key, issue_number)

    @validates('shareable_booking_id')
    def _validate_shareable_booking_id(self, key, shareable_booking_id):
        return self.get_validator(key, shareable_booking_id)

    @validates('status')
    def _validate_status(self, key, status):
        return self.get_validator(key, status)

    @validates('issue_link')
    def _validate_issue_link(self, key, issue_link):
        return self.get_validator(key, issue_link)

    @validates('auto_detach_status')
    def _validate_auto_detach_status(self, key, auto_detach_status):
        return self.get_validator(key, auto_detach_status)


class OrganizationConstraint(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'organization_constraint'

    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False, info=ColumnPermissions.create_only)
    type = Column(OrganizationConstraintType('type'),
                  default=OrganizationConstraintTypes.EXPENSE_ANOMALY,
                  nullable=False, info=ColumnPermissions.create_only)
    definition = Column(ConstraintDefinition('definition'), nullable=False,
                        info=ColumnPermissions.create_only)
    filters = Column(ConstraintDefinition('filters'), nullable=False,
                     info=ColumnPermissions.create_only)
    last_run = Column(NullableInt('last_run'), default=0,
                      nullable=False, info=ColumnPermissions.update_only)
    last_run_result = Column(RunResult('last_run_result'),
                             info=ColumnPermissions.update_only,
                             nullable=False, default='{}')

    @validates('name', 'organization_id', 'type', 'definition', 'filters',
               'last_run', 'last_run_result')
    def _validate_params(self, key, name):
        return self.get_validator(key, name)

    @hybrid_property
    def loaded_filters(self):
        return json.loads(self.filters)

    def to_dict(self):
        constr_dict = super().to_dict()
        for f in ['definition', 'filters', 'last_run_result']:
            if isinstance(constr_dict[f], str):
                constr_dict[f] = json.loads(constr_dict[f])
        if hasattr(self, 'limit_hits'):
            # pylint: disable=no-member
            constr_dict['limit_hits'] = [x.to_dict() for x in self.limit_hits]
        return constr_dict


class OrganizationLimitHit(Base, MutableMixin, ValidatorMixin):
    __tablename__ = 'organization_limit_hit'

    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False, info=ColumnPermissions.create_only)
    constraint_id = Column(Uuid('constraint_id'),
                           ForeignKey('organization_constraint.id'),
                           nullable=False,
                           info=ColumnPermissions.create_only)
    constraint_limit = Column(Float('constraint_limit'), nullable=False,
                              info=ColumnPermissions.full)
    value = Column(Float('value'), nullable=False,
                   info=ColumnPermissions.full)
    created_at = Column(Integer, default=now_timestamp, nullable=False,
                        info=ColumnPermissions.create_only)
    run_result = Column(RunResult('run_result'),
                        info=ColumnPermissions.full,
                        nullable=False, default='{}')

    __table_args__ = (UniqueConstraint(
        "constraint_id", "created_at",
        name="uc_constraint_id_created_at"),)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'created_at' not in kwargs:
            self.created_at = now_timestamp()

    @validates('organization_id', 'constraint_id', 'constraint_limit',
               'value', 'run_result')
    def _validate_params(self, key, organization_id):
        return self.get_validator(key, organization_id)

    def to_dict(self):
        res = super().to_dict()
        if isinstance(res['run_result'], str):
            res['run_result'] = json.loads(res['run_result'])
        return res


class TrafficProcessingTask(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'traffic_processing_task'

    cloud_account_id = Column(
        Uuid('cloud_account_id'), ForeignKey('cloudaccount.id'),
        nullable=False, info=ColumnPermissions.create_only)
    start_date = Column(Int('start_date'), nullable=False,
                        info=ColumnPermissions.create_only)
    end_date = Column(Int('end_date'), nullable=False,
                      info=ColumnPermissions.create_only)

    __table_args__ = (UniqueConstraint(
        "cloud_account_id", "start_date", "end_date", "deleted_at",
        name="uc_acc_id_start_end_deleted_at"),)

    @validates('cloud_account_id')
    def _validate_cloud_account_id(self, key, cloud_account_id):
        return self.get_validator(key, cloud_account_id)

    @validates('start_date')
    def _validate_start_date(self, key, start_date):
        return self.get_validator(key, start_date)

    @validates('end_date')
    def _validate_end_date(self, key, end_date):
        return self.get_validator(key, end_date)


class RispProcessingTask(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'risp_processing_task'

    cloud_account_id = Column(
        Uuid('cloud_account_id'), ForeignKey('cloudaccount.id'),
        nullable=False, info=ColumnPermissions.create_only)
    start_date = Column(Int('start_date'), nullable=False,
                        info=ColumnPermissions.create_only)
    end_date = Column(Int('end_date'), nullable=False,
                      info=ColumnPermissions.create_only)

    __table_args__ = (UniqueConstraint(
        "cloud_account_id", "start_date", "end_date", "deleted_at",
        name="uc_acc_id_start_end_deleted_at"),)

    @validates('cloud_account_id')
    def _validate_cloud_account_id(self, key, cloud_account_id):
        return self.get_validator(key, cloud_account_id)

    @validates('start_date')
    def _validate_start_date(self, key, start_date):
        return self.get_validator(key, start_date)

    @validates('end_date')
    def _validate_end_date(self, key, end_date):
        return self.get_validator(key, end_date)


class ProfilingToken(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = 'profiling_token'

    organization_id = Column(
        Uuid('organization_id'), ForeignKey('organization.id'), nullable=False,
        info=ColumnPermissions.create_only)
    token = Column(NullableUuid('token'), nullable=False, default=gen_id)
    infrastructure_token = Column(NullableUuid('infrastructure_token'),
                                  nullable=False, default=gen_id)
    __table_args__ = (UniqueConstraint(
        "organization_id", "deleted_at", name="organization_deleted_at"),)

    @hybrid_property
    def unique_fields(self):
        return ['organization_id']

    @validates('organization_id')
    def _validate_organization_id(self, key, organization_id):
        return self.get_validator(key, organization_id)

    def to_dict(self):
        res = super().to_dict()
        res.pop('infrastructure_token', None)
        return res


class OrganizationBI(CreatedMixin, ImmutableMixin, ValidatorMixin, Base):
    __tablename__ = 'organization_bi'

    organization_id = Column(Uuid('organization_id'),
                             ForeignKey('organization.id'),
                             nullable=False,
                             info=ColumnPermissions.create_only)
    type = Column(BIType('type'),
                  nullable=False, info=ColumnPermissions.create_only)
    name = Column(BaseString('name'), nullable=False,
                  info=ColumnPermissions.full)
    days = Column(Int('days'), nullable=False, info=ColumnPermissions.full)
    last_run = Column(Int('last_run'), default=0,
                      nullable=False, info=ColumnPermissions.update_only)
    next_run = Column(Int('next_run'), default=now_timestamp,
                      nullable=False, info=ColumnPermissions.update_only)
    last_completed = Column(Int('last_completed'), default=0,
                            nullable=False, info=ColumnPermissions.update_only)
    status = Column(BIOrganizationStatus,
                    default=BIOrganizationStatuses.ACTIVE,
                    nullable=False, info=ColumnPermissions.update_only)
    last_status_error = Column(NullableText('last_status_error'), nullable=True,
                               info=ColumnPermissions.update_only)
    meta = Column(NullableText('meta'), nullable=False,
                  info=ColumnPermissions.full)

    __table_args__ = (UniqueConstraint(
        "organization_id", "name", "deleted_at",
        name="uc_organization_id_name_deleted_at"),)

    @hybrid_property
    def unique_fields(self):
        return ['organization_id', 'name']

    @validates('organization_id', 'type', 'name', 'days', 'last_run',
               'next_run', 'last_completed', 'status', 'meta',
               'last_status_error')
    def _validate(self, key, value):
        return self.get_validator(key, value)

    @staticmethod
    def _get_files_paths(bi_id, bi_type, bi_meta):
        files = []
        for file_type in ['expenses', 'recommendations', 'resources']:
            filename = '_'.join([bi_id, file_type]) + '.csv'
            if bi_type == BITypes.AZURE_RAW_EXPORT.value:
                path = '/'.join([bi_meta['storage_account'],
                                 bi_meta['container'],
                                 filename])
            elif bi_type == BITypes.AWS_RAW_EXPORT.value:
                if bi_meta.get('s3_path'):
                    params = [bi_meta['bucket'], bi_meta['s3_path'], file_type,
                              filename]
                else:
                    params = [bi_meta['bucket'], file_type, filename]
                path = '/'.join(params)
            else:
                raise WrongArgumentsException(Err.OE0217, ['type'])
            files.append(path)
        return files

    def to_dict(self, secure=False, with_files=False):
        bi_dict = super().to_dict()
        bi_dict['type'] = bi_dict['type'].value
        bi_dict['meta'] = json.loads(decrypt_bi_meta(bi_dict['meta']))
        if secure:
            for k in ['connection_string', 'secret_access_key']:
                bi_dict['meta'].pop(k, None)
        if with_files:
            bi_dict['files'] = self._get_files_paths(
                bi_dict['id'], bi_dict['type'], bi_dict['meta'])
        return bi_dict

    def to_json(self, secure=True, with_files=False):
        return json.dumps(self.to_dict(secure=secure, with_files=with_files),
                          cls=ModelEncoder)


class OrganizationGemini(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = "organization_gemini"

    organization_id = Column(Uuid("organization_id"),
                             ForeignKey("organization.id"),
                             nullable=False,
                             info=ColumnPermissions.create_only)
    last_run = Column(Int("last_run"), default=0,
                      nullable=False, info=ColumnPermissions.update_only)
    last_completed = Column(Int("last_completed"), default=0,
                            nullable=False, info=ColumnPermissions.update_only)
    last_error = Column(NullableText("last_error"), nullable=True,
                        info=ColumnPermissions.update_only)
    status = Column(GeminiStatus,
                    default=GeminiStatuses.CREATED,
                    nullable=False, info=ColumnPermissions.update_only)
    filters = Column(NullableText("filters"), nullable=True,
                     info=ColumnPermissions.create_only, default="{}")
    stats = Column(NullableText("stats"), nullable=True,
                   info=ColumnPermissions.full, default="{}")

    @hybrid_property
    def unique_fields(self):
        return ["organization_id"]

    @validates("organization_id", "last_run", "last_completed",
               "last_error", "status", "filters", "stats")
    def _validate(self, key, value):
        return self.get_validator(key, value)

    def to_dict(self):
        res = super().to_dict()
        res["filters"] = json.loads(res.pop("filters"))
        res["stats"] = json.loads(res.pop("stats"))
        return res


class PowerSchedule(Base, CreatedMixin, ImmutableMixin, ValidatorMixin):
    __tablename__ = "power_schedule"

    organization_id = Column(Uuid("organization_id"),
                             ForeignKey("organization.id"), nullable=False,
                             info=ColumnPermissions.create_only)
    name = Column(BaseString('name'), nullable=False,
                  info=ColumnPermissions.full)
    power_off = Column(HMTimeString('power_off'), nullable=False,
                       info=ColumnPermissions.full)
    power_on = Column(HMTimeString('power_on'), nullable=False,
                      info=ColumnPermissions.full)
    timezone = Column(TimezoneString('timezone'), nullable=False,
                      info=ColumnPermissions.full)
    enabled = Column(NullableBool('enabled'), nullable=False,
                     info=ColumnPermissions.full)
    start_date = Column(NullableInt("start_date"), default=0, nullable=False,
                        info=ColumnPermissions.full)
    end_date = Column(NullableInt("end_date"), default=0,
                      nullable=False, info=ColumnPermissions.full)
    last_eval = Column(Int("last_eval"), default=0,
                       nullable=False, info=ColumnPermissions.update_only)
    last_run = Column(Int("last_run"), default=0,
                      nullable=False, info=ColumnPermissions.update_only)
    last_run_error = Column(NullableText("last_run_error"), nullable=True,
                            info=ColumnPermissions.update_only)

    __table_args__ = (UniqueConstraint(
        "organization_id", "name", "deleted_at",
        name="uc_organization_id_name_deleted_at"),)

    @hybrid_property
    def unique_fields(self):
        return ['organization_id', 'name']

    @validates('organization_id', 'name', 'power_off', 'power_on', 'timezone',
               'enabled', 'start_date', 'end_date', 'last_eval', 'last_run',
               'last_run_error')
    def _validate(self, key, value):
        return self.get_validator(key, value)


class Layout(Base, BaseMixin, ValidatorMixin):
    __tablename__ = 'layout'
    id = Column(NullableUuid('id'), primary_key=True, default=gen_id,
                info=ColumnPermissions.create_only)
    name = Column(NotWhiteSpaceString('name'), nullable=False,
                  info=ColumnPermissions.full)
    data = Column(NullableJSON('data'), nullable=False, default='{}',
                  info=ColumnPermissions.full)
    type = Column(NotWhiteSpaceString('type'), nullable=False,
                  info=ColumnPermissions.create_only)
    shared = Column(NullableBool('shared'), nullable=False, default=False,
                    info=ColumnPermissions.full)
    owner_id = Column(Uuid('owner_id'),
                      ForeignKey('employee.id'),
                      info=ColumnPermissions.full,
                      nullable=False)
    owner = relationship("Employee", foreign_keys=[owner_id])
    entity_id = Column(NullableUuid('entity_id'), nullable=True,
                       info=ColumnPermissions.create_only)

    @validates("name", "data", "type", "shared", "owner_id", "entity_id")
    def _validate(self, key, value):
        return self.get_validator(key, value)

    @hybrid_property
    def deleted(self):
        return false()
