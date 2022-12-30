""""initial"

Revision ID: 5a121c63e3f2
Revises: 
Create Date: 2022-11-22 09:20:25.346835

"""
from alembic import op
import sqlalchemy as sa

import rest_api_server.models


# revision identifiers, used by Alembic.
revision = '5a121c63e3f2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table('organization',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.AutogenUuid(length=36), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.NullableUuid(length=36), nullable=True),
    sa.Column('is_demo', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('currency', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('employee',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('name', rest_api_server.models.types.Name(length=256), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('auth_user_id', rest_api_server.models.types.NullableUuid(length=36), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'auth_user_id', 'deleted_at', name='uc_employee_org_auth_user')
    )

    op.create_table('pool',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('limit', rest_api_server.models.types.BigInt(), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('parent_id', rest_api_server.models.types.NullableUuid(length=36), nullable=True),
    sa.Column('purpose', sa.Enum('BUDGET', 'BUSINESS_UNIT', 'TEAM', 'PROJECT', 'CICD', 'MLAI', 'ASSET_POOL'), nullable=False),
    sa.Column('default_owner_id', rest_api_server.models.types.NullableUuid(length=36), nullable=True),
    sa.ForeignKeyConstraint(['default_owner_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'deleted_at', 'parent_id', 'organization_id', name='uc_name_del_at_parent_id_organization_id')
    )

    op.create_table('pool_alert',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('threshold', sa.Integer(), nullable=False),
    sa.Column('threshold_type', sa.Enum('ABSOLUTE', 'PERCENTAGE'), nullable=False),
    sa.Column('based', sa.Enum('COST', 'FORECAST', 'CONSTRAINT', 'ENV_CHANGE'), nullable=False),
    sa.Column('last_shoot_at', sa.Integer(), nullable=False),
    sa.Column('include_children', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('alert_contact',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('pool_alert_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('employee_id', rest_api_server.models.types.Uuid(length=36), nullable=True),
    sa.Column('slack_channel_id', rest_api_server.models.types.Uuid(length=36), nullable=True),
    sa.Column('slack_team_id', rest_api_server.models.types.Uuid(length=36), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['pool_alert_id'], ['pool_alert.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('assignment_request',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('resource_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('source_pool_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('message', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.Column('approver_id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('requester_id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'DECLINED', 'CANCELED'), nullable=False),
    sa.ForeignKeyConstraint(['approver_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['source_pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('resource_id', 'deleted_at', name='uc_resource_id_deleted_at')
    )
    op.create_index(op.f('ix_assignment_request_resource_id'), 'assignment_request', ['resource_id'], unique=False)

    op.create_table('calendar_synchronization',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('calendar_id', rest_api_server.models.types.BaseString(length=256), nullable=False),
    sa.Column('last_completed', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('deleted_at', 'organization_id', name='uc_org_id_deleted_at')
    )

    op.create_table('checklist',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('last_run', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('next_run', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_completed', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('deleted_at', 'organization_id', name='uc_del_at_org_id')
    )

    op.create_table('cost_model',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('type', sa.Enum('CLOUD_ACCOUNT', 'RESOURCE'), nullable=False),
    sa.Column('value', rest_api_server.models.types.NullableJSON(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('cloudaccount',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('type', sa.Enum('AWS_CNR', 'ALIBABA_CNR', 'AZURE_CNR', 'KUBERNETES_CNR', 'ENVIRONMENT'), nullable=False),
    sa.Column('config', rest_api_server.models.types.NullableText(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('cost_model_id', rest_api_server.models.types.Uuid(length=36), nullable=True),
    sa.Column('auto_import', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('import_period', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_import_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_import_modified_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('account_id', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.Column('process_recommendations', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('last_import_attempt_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_import_attempt_error', rest_api_server.models.types.NullableText(), nullable=True),
    sa.ForeignKeyConstraint(['cost_model_id'], ['cost_model.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id', 'type', 'organization_id', 'deleted_at', name='uc_account_type_org_id_del_at'),
    sa.UniqueConstraint('organization_id', 'name', 'deleted_at', name='uc_org_name_del_at')
    )

    op.create_table('cluster_type',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('name', rest_api_server.models.types.Name(length=256), nullable=False),
    sa.Column('tag_key', rest_api_server.models.types.BaseString(length=256), nullable=False),
    sa.Column('priority', rest_api_server.models.types.Int(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'deleted_at', 'organization_id', name='uc_name_del_at_org_id'),
    sa.UniqueConstraint('priority', 'deleted_at', 'organization_id', name='uc_priority_del_at_org_id')
    )

    op.create_table('rule',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('name', rest_api_server.models.types.Name(length=256), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('creator_id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('owner_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'deleted_at', 'organization_id', name='uc_name_del_at_org_id'),
    sa.UniqueConstraint('priority', 'deleted_at', 'organization_id', name='uc_priority_del_at_org_id')
    )

    op.create_table('condition',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('NAME_IS', 'NAME_STARTS_WITH', 'NAME_ENDS_WITH', 'NAME_CONTAINS',
                              'RESOURCE_TYPE_IS', 'CLOUD_IS', 'TAG_IS', 'REGION_IS', 'TAG_EXISTS',
                              'TAG_VALUE_STARTS_WITH'), nullable=False),
    sa.Column('rule_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('meta_info', rest_api_server.models.types.BaseString(length=256), nullable=False),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('constraint_limit_hit',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('resource_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.NullableUuid(length=36), nullable=True),
    sa.Column('type', sa.Enum('TTL', 'TOTAL_EXPENSE_LIMIT', 'DAILY_EXPENSE_LIMIT'), nullable=False),
    sa.Column('constraint_limit', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('ttl_value', rest_api_server.models.types.NullableInt(), nullable=True),
    sa.Column('expense_value', rest_api_server.models.types.NullableFloat(), nullable=True),
    sa.Column('time', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('state', sa.Enum('RED', 'GREEN'), nullable=False),
    sa.CheckConstraint('(ttl_value IS NULL) <> (expense_value IS NULL)', name='hit_value_xor'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_constraint_limit_hit_resource_id'), 'constraint_limit_hit', ['resource_id'], unique=False)

    op.create_table('discovery_info',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('cloud_account_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('resource_type', sa.Enum('instance', 'volume', 'snapshot', 'bucket', 'k8s_pod',
                                       'snapshot_chain', 'rds_instance', 'ip_address'), nullable=False),
    sa.Column('observe_time', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_discovery_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_error_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_error', rest_api_server.models.types.NullableText(), nullable=True),
    sa.Column('enabled', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cloud_account_id', 'resource_type', 'deleted_at', name='uc_cloud_acc_id_del_at')
    )

    op.create_table('expenses_export',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('deleted_at', 'pool_id', name='uc_pool_id_deleted_at')
    )

    op.create_table('invite',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('email', rest_api_server.models.types.Email(length=256), nullable=False),
    sa.Column('owner_id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('ttl', sa.Integer(), nullable=False),
    sa.Column('meta', rest_api_server.models.types.NullableMetadata(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('invite_assignment',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('invite_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('scope_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('scope_type', sa.Enum('ORGANIZATION', 'POOL'), nullable=False),
    sa.Column('purpose', sa.Enum('optscale_member', 'optscale_engineer', 'optscale_manager'), nullable=False),
    sa.ForeignKeyConstraint(['invite_id'], ['invite.id'], ),
    sa.PrimaryKeyConstraint('id', 'invite_id', 'scope_id'),
    sa.UniqueConstraint('invite_id', 'scope_id', name='uc_invite_id_scope_id')
    )

    op.create_table('shareable_booking',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('resource_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('acquired_by_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('acquired_since', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('released_at', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('ssh_key', rest_api_server.models.types.NullableJSON(), nullable=True),
    sa.Column('jira_auto_release', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('event_id', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.ForeignKeyConstraint(['acquired_by_id'], ['employee.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'event_id', name='uc_calendar_id_event_id')
    )

    op.create_table('jira_issue_attachment',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('client_key', rest_api_server.models.types.MediumLargeNullableString(length=128), nullable=False),
    sa.Column('project_key', rest_api_server.models.types.BaseString(length=256), nullable=False),
    sa.Column('issue_number', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('shareable_booking_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('status', rest_api_server.models.types.MediumString(length=60), nullable=False),
    sa.Column('issue_link', rest_api_server.models.types.NullableText(), nullable=False),
    sa.Column('auto_detach_status', rest_api_server.models.types.MediumNullableString(length=60), nullable=True),
    sa.ForeignKeyConstraint(['shareable_booking_id'], ['shareable_booking.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('shareable_booking_id', 'client_key', 'project_key', 'issue_number', 'deleted_at',
                        name='uc_book_id_client_project_issue_deleted_at')
    )

    op.create_table('k8s_node',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('cloud_account_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('last_seen', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('flavor', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.Column('cpu', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('memory', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('provider_id', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.Column('hourly_price', rest_api_server.models.types.NullableFloat(), nullable=True),
    sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cloud_account_id', 'name', 'provider_id', 'deleted_at',
                        name='uc_cloud_acc_id_name_provider_id_deleted_at')
    )

    op.create_table('organization_constraint',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('type', sa.Enum('EXPENSE_ANOMALY', 'EXPIRING_BUDGET', 'RECURRING_BUDGET',
                              'RESOURCE_COUNT_ANOMALY', 'RESOURCE_QUOTA', 'TAGGING_POLICY'), nullable=False),
    sa.Column('definition', rest_api_server.models.types.ConstraintDefinition(), nullable=False),
    sa.Column('filters', rest_api_server.models.types.ConstraintDefinition(), nullable=False),
    sa.Column('last_run', rest_api_server.models.types.NullableInt(), nullable=False),
    sa.Column('last_run_result', rest_api_server.models.types.RunResult(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('organization_limit_hit',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('constraint_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('constraint_limit', rest_api_server.models.types.Float(), nullable=False),
    sa.Column('value', rest_api_server.models.types.Float(), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('run_result', rest_api_server.models.types.RunResult(), nullable=False),
    sa.ForeignKeyConstraint(['constraint_id'], ['organization_constraint.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('constraint_id', 'created_at', name='uc_constraint_id_created_at')
    )

    op.create_table('organization_option',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('value', rest_api_server.models.types.NullableMetadata(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pool_policy',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('TTL', 'TOTAL_EXPENSE_LIMIT', 'DAILY_EXPENSE_LIMIT'), nullable=False),
    sa.Column('limit', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('active', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('pool_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type', 'pool_id', 'deleted_at', name='uc_name_del_at_parent_id')
    )

    op.create_table('reportimport',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('cloud_account_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('import_file', rest_api_server.models.types.NullableString(length=256), nullable=True),
    sa.Column('state', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'FAILED'), nullable=False),
    sa.Column('state_reason', rest_api_server.models.types.NullableText(), nullable=True),
    sa.Column('is_recalculation', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('resource_constraint',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('TTL', 'TOTAL_EXPENSE_LIMIT', 'DAILY_EXPENSE_LIMIT'), nullable=False),
    sa.Column('limit', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('resource_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type', 'resource_id', 'deleted_at', name='uc_name_del_at_parent_id')
    )
    op.create_index(op.f('ix_resource_constraint_resource_id'), 'resource_constraint', ['resource_id'], unique=False)


    op.create_index(op.f('ix_shareable_booking_resource_id'), 'shareable_booking', ['resource_id'], unique=False)
    op.create_table('ssh_key',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('name', rest_api_server.models.types.NotWhiteSpaceString(length=256), nullable=False),
    sa.Column('employee_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('default', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('fingerprint', rest_api_server.models.types.NullableString(length=256), nullable=False),
    sa.Column('key', rest_api_server.models.types.BaseText(), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_id', 'fingerprint', 'deleted_at', name='uc_employee_id_fingerprint_deleted_at')
    )

    op.create_table('traffic_processing_task',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('cloud_account_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('start_date', rest_api_server.models.types.Int(), nullable=False),
    sa.Column('end_date', rest_api_server.models.types.Int(), nullable=False),
    sa.ForeignKeyConstraint(['cloud_account_id'], ['cloudaccount.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cloud_account_id', 'start_date', 'end_date', 'deleted_at',
                        name='uc_acc_id_start_end_deleted_at')
    )

    op.create_table('webhook',
    sa.Column('deleted_at', sa.Integer(), nullable=False),
    sa.Column('id', rest_api_server.models.types.NullableUuid(length=36), nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('organization_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('object_type', sa.Enum('ENVIRONMENT'), nullable=False),
    sa.Column('object_id', rest_api_server.models.types.Uuid(length=36), nullable=False),
    sa.Column('active', rest_api_server.models.types.NullableBool(), nullable=False),
    sa.Column('action', sa.Enum('BOOKING_ACQUIRE', 'BOOKING_RELEASE'), nullable=False),
    sa.Column('url', rest_api_server.models.types.NullableText(), nullable=False),
    sa.Column('headers', rest_api_server.models.types.NullableJSON(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'deleted_at', 'object_id', 'action',
                        name='uc_org_id_deleted_at_obj_id_action')
    )
    op.create_index(op.f('ix_webhook_object_id'), 'webhook', ['object_id'], unique=False)

    op.create_foreign_key('organization_pool_fk', 'organization', 'pool',
                          ['pool_id'], ['id'])


def downgrade():
    op.drop_index(op.f('ix_webhook_object_id'), table_name='webhook')
    op.drop_table('webhook')
    op.drop_table('traffic_processing_task')
    op.drop_table('ssh_key')
    op.drop_index(op.f('ix_resource_constraint_resource_id'), table_name='resource_constraint')
    op.drop_table('resource_constraint')
    op.drop_table('reportimport')
    op.drop_table('pool_policy')
    op.drop_table('organization_option')
    op.drop_table('organization_limit_hit')
    op.drop_table('organization_constraint')
    op.drop_table('k8s_node')
    op.drop_table('jira_issue_attachment')
    op.drop_index(op.f('ix_shareable_booking_resource_id'), table_name='shareable_booking')
    op.drop_table('shareable_booking')
    op.drop_table('invite_assignment')
    op.drop_table('invite')
    op.drop_table('expenses_export')
    op.drop_table('discovery_info')
    op.drop_index(op.f('ix_constraint_limit_hit_resource_id'), table_name='constraint_limit_hit')
    op.drop_table('constraint_limit_hit')
    op.drop_table('condition')
    op.drop_table('rule')
    op.drop_table('cluster_type')
    op.drop_table('cloudaccount')
    op.drop_table('cost_model')
    op.drop_table('calendar_synchronization')
    op.drop_table('checklist')
    op.drop_index(op.f('ix_assignment_request_resource_id'), table_name='assignment_request')
    op.drop_table('assignment_request')
    op.drop_table('alert_contact')
    op.drop_table('pool_alert')
    op.drop_constraint(op.f('organization_pool_fk'), table_name='organization', type_='foreignkey')
    op.drop_table('pool')
    op.drop_table('employee')
    op.drop_table('organization')
