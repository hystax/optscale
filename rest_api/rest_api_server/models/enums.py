import enum


class CloudTypes(enum.Enum):
    AWS_CNR = 'aws_cnr'
    ALIBABA_CNR = 'alibaba_cnr'
    AZURE_CNR = 'azure_cnr'
    AZURE_TENANT = 'azure_tenant'
    KUBERNETES_CNR = 'kubernetes_cnr'
    ENVIRONMENT = 'environment'
    GCP_CNR = 'gcp_cnr'
    NEBIUS = 'nebius'


class ImportStates(enum.Enum):
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'


class RolePurposes(enum.Enum):
    optscale_member = 'optscale_member'
    optscale_engineer = 'optscale_engineer'
    optscale_manager = 'optscale_manager'


class AssignmentRequestStatuses(enum.Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    CANCELED = 'CANCELED'


class ThresholdTypes(enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENTAGE = 'percentage'


class ThresholdBasedTypes(enum.Enum):
    COST = 'cost'
    FORECAST = 'forecast'
    CONSTRAINT = 'constraint'
    ENV_CHANGE = 'env_change'


class AssignmentRequestTypes(enum.Enum):
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'


class ConditionTypes(enum.Enum):
    NAME_IS = 'name_is'
    NAME_STARTS_WITH = 'name_starts_with'
    NAME_ENDS_WITH = 'name_ends_with'
    NAME_CONTAINS = 'name_contains'
    RESOURCE_TYPE_IS = 'resource_type_is'
    CLOUD_IS = 'cloud_is'
    TAG_IS = 'tag_is'
    REGION_IS = 'region_is'
    TAG_EXISTS = 'tag_exists'
    TAG_VALUE_STARTS_WITH = 'tag_value_starts_with'

    @classmethod
    # pylint: disable=E1101
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    # pylint: disable=E1101
    def complex_types(cls):
        return [cls.TAG_IS.value, cls.TAG_VALUE_STARTS_WITH.value]


class CostModelTypes(enum.Enum):
    CLOUD_ACCOUNT = 'cloud_account'
    RESOURCE = 'resource'


class ConstraintTypes(enum.Enum):
    TTL = 'ttl'
    TOTAL_EXPENSE_LIMIT = 'total_expense_limit'
    DAILY_EXPENSE_LIMIT = 'daily_expense_limit'


class ConstraintLimitStates(enum.Enum):
    RED = 'red'
    GREEN = 'green'


class OrganizationConstraintTypes(enum.Enum):
    EXPENSE_ANOMALY = 'expense_anomaly'
    EXPIRING_BUDGET = 'expiring_budget'
    RECURRING_BUDGET = 'recurring_budget'
    RESOURCE_COUNT_ANOMALY = 'resource_count_anomaly'
    RESOURCE_QUOTA = 'resource_quota'
    TAGGING_POLICY = 'tagging_policy'


class LimitHitsSelector(enum.Enum):
    resource_id = 'resource_id'
    pool_id = 'pool_id'


class PoolPurposes(enum.Enum):
    BUDGET = 'budget'
    BUSINESS_UNIT = 'business_unit'
    TEAM = 'team'
    PROJECT = 'project'
    CICD = 'cicd'
    MLAI = 'mlai'
    ASSET_POOL = 'asset_pool'


class InviteAssignmentScopeTypes(enum.Enum):
    ORGANIZATION = 'organization'
    POOL = 'pool'


class WebhookObjectTypes(enum.Enum):
    ENVIRONMENT = 'environment'


class WebhookActionTypes(enum.Enum):
    BOOKING_ACQUIRE = 'booking_acquire'
    BOOKING_RELEASE = 'booking_release'


class AuthenticationType(enum.Enum):
    GOOGLE = 'google'
    PASSWORD = 'password'


class RunStates(enum.IntEnum):
    running = 1
    completed = 2
    failed = 3
    aborted = 4


class BITypes(str, enum.Enum):
    AWS_RAW_EXPORT = 'AWS_RAW_EXPORT'
    AZURE_RAW_EXPORT = 'AZURE_RAW_EXPORT'


class BIOrganizationStatuses(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCESS = 'SUCCESS'
