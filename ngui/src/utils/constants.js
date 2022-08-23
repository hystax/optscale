// Roles
export const ORGANIZATION_MANAGER = "organization_optscale_manager"; // Not a real role, just to distinguish from a Pool manager
export const MANAGER = "optscale_manager";
export const ENGINEER = "optscale_engineer";
export const MEMBER = "optscale_member";

export const ROLE_PURPOSES = Object.freeze({
  [ORGANIZATION_MANAGER]: "organizationManager",
  [MANAGER]: "manager",
  [ENGINEER]: "engineer",
  [MEMBER]: "member"
});

export const ORGANIZATION_ROLE_PURPOSES = Object.freeze({
  [MANAGER]: "organizationManager",
  [ENGINEER]: "organizationEngineer",
  [MEMBER]: "member"
});

// Pool purposes
export const POOL_TYPE_BUDGET = "budget";
export const POOL_TYPE_BUSINESS_UNIT = "business_unit";
export const POOL_TYPE_TEAM = "team";
export const POOL_TYPE_PROJECT = "project";
export const POOL_TYPE_CICD = "cicd";
export const POOL_TYPE_MLAI = "mlai";
export const POOL_TYPE_ASSET_POOL = "asset_pool";

export const POOL_TYPES = Object.freeze({
  [POOL_TYPE_BUDGET]: POOL_TYPE_BUDGET,
  [POOL_TYPE_BUSINESS_UNIT]: "businessUnit",
  [POOL_TYPE_TEAM]: POOL_TYPE_TEAM,
  [POOL_TYPE_PROJECT]: POOL_TYPE_PROJECT,
  [POOL_TYPE_CICD]: POOL_TYPE_CICD,
  [POOL_TYPE_MLAI]: POOL_TYPE_MLAI,
  [POOL_TYPE_ASSET_POOL]: "assetPool"
});

// Assignment Request actions
export const ACCEPT = "accept";
export const DECLINE = "decline";
export const CANCEL = "cancel";

// Data Sources
export const AWS_CNR = "aws_cnr";
export const AZURE_CNR = "azure_cnr";
export const GCP_CNR = "gcp_cnr";
export const KUBERNETES_CNR = "kubernetes_cnr";
export const ALIBABA_CNR = "alibaba_cnr";
export const ENVIRONMENT = "environment";

export const AWS_ROOT_ACCOUNT = "awsRoot";
export const AWS_LINKED_ACCOUNT = "awsLinked";
export const AZURE_SUBSCRIPTION = "azure";
export const KUBERNETES = "kubernetes";
export const ALIBABA_ACCOUNT = "alibaba";

export const DATASOURCE_TYPE = "type";

export const NOT_SET_CLOUD_TYPE = "not_set";

// Expenses
export const LAST_MONTH = "last_month";
export const THIS_MONTH = "this_month";
export const THIS_MONTH_FORECAST = "this_month_forecast";

export const EXPENSES_PERIOD = Object.freeze({
  [LAST_MONTH]: "lastMonth",
  [THIS_MONTH]: "thisMonth",
  [THIS_MONTH_FORECAST]: "thisMonthForecast"
});

export const COST_EXPLORER = "COST_EXPLORER";
export const CLOUD_DETAILS = "CLOUD_DETAILS";
export const OWNER_DETAILS = "OWNER_DETAILS";
export const POOL_DETAILS = "POOL_DETAILS";

export const FILTER_BY = "filterBy";

export const EXPENSES_FILTERBY_TYPES = Object.freeze({
  CLOUD: "cloud",
  POOL: "pool",
  EMPLOYEE: "employee",
  SERVICE: "service",
  REGION: "region",
  RESOURCE_TYPE: "resource_type",
  NODE: "k8s_node",
  NAMESPACE: "k8s_namespace"
});

// Split resources
export const OWNED = "owned";
export const MANAGED = "managed";
export const RESTRICTED = "restricted";

// Assignment requests
export const REQUESTED = "requested";

// Assignment rules
export const NAME_ID_STARTS_WITH = "name_starts_with";
export const NAME_ID_ENDS_WITH = "name_ends_with";
export const NAME_ID_IS = "name_is";
export const NAME_ID_CONTAINS = "name_contains";
export const TAG_IS = "tag_is";
export const CLOUD_IS = "cloud_is";
export const TAG_EXISTS = "tag_exists";
export const TAG_VALUE_STARTS_WITH = "tag_value_starts_with";

export const COMPLEX_TAG_CONDITION_TYPES = Object.freeze({
  [TAG_IS]: "tagIs",
  [TAG_VALUE_STARTS_WITH]: "tagValueStartsWith"
});

export const CONDITION_TYPES = Object.freeze({
  [NAME_ID_STARTS_WITH]: "nameIdStartsWith",
  [NAME_ID_ENDS_WITH]: "nameIdEndsWith",
  [NAME_ID_IS]: "nameIdIs",
  [NAME_ID_CONTAINS]: "nameIdContains",
  [TAG_IS]: "tagIs",
  [TAG_EXISTS]: "tagExists",
  [TAG_VALUE_STARTS_WITH]: "tagValueStartsWith",
  [CLOUD_IS]: "sourceIs"
});

export const CONDITION = Object.freeze({
  META_INFO: "meta_info",
  TYPE: "type"
});

export const TAG_CONDITION = Object.freeze({
  KEY: "key",
  VALUE: "value"
});

export const CLOUD_IS_CONDITION_VALUE = "cloudId";

export const DEFAULT_CONDITION = {
  [CONDITION.TYPE]: NAME_ID_STARTS_WITH,
  [CONDITION.META_INFO]: ""
};

export const DEFAULT_CONDITIONS = [DEFAULT_CONDITION];

// Statuses
export const INFO = "info";
export const WARNING = "warning";
export const ERROR = "error";
export const SUCCESS = "success";
export const UNKNOWN = "unknown";

// Tasks
export const TASK_INCOMING_ASSIGNMENT_REQUESTS = "incomingAssignmentRequests";
export const INCOMING_ASSIGNMENT_REQUESTS_TYPE = "incoming_assignment_requests";

export const TASK_OUTGOING_ASSIGNMENT_REQUESTS = "outgoingAssignmentRequests";
export const OUTGOING_ASSIGNMENT_REQUESTS_TYPE = "outgoing_assignment_requests";

export const TASK_EXCEEDED_POOLS = "exceededPools";
export const EXCEEDED_POOLS_TYPE = "exceeded_pools";

export const TASK_EXCEEDED_POOL_FORECASTS = "exceededPoolForecasts";
export const EXCEEDED_POOL_FORECASTS_TYPE = "exceeded_pool_forecasts";

export const TASK_VIOLATED_RESOURCE_CONSTRAINTS = "violatedResourceConstraints";
export const VIOLATED_RESOURCE_CONSTRAINTS_TYPE = "violated_constraints";

export const TASK_VIOLATED_ORGANIZATION_CONSTRAINTS = "violatedOrganizationConstraints";
export const VIOLATED_ORGANIZATION_CONSTRAINTS_TYPE = "violated_organization_constraints";

export const TASK_DIVERGENT_CONSTRAINTS = "divergentConstraints";
export const DIVERGENT_CONSTRAINTS_TYPE = "differ_constraints";

export const MAP_MY_TASKS_TYPES = Object.freeze({
  [INCOMING_ASSIGNMENT_REQUESTS_TYPE]: TASK_INCOMING_ASSIGNMENT_REQUESTS,
  [OUTGOING_ASSIGNMENT_REQUESTS_TYPE]: TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  [EXCEEDED_POOLS_TYPE]: TASK_EXCEEDED_POOLS,
  [EXCEEDED_POOL_FORECASTS_TYPE]: TASK_EXCEEDED_POOL_FORECASTS,
  [VIOLATED_RESOURCE_CONSTRAINTS_TYPE]: TASK_VIOLATED_RESOURCE_CONSTRAINTS,
  [VIOLATED_ORGANIZATION_CONSTRAINTS_TYPE]: TASK_VIOLATED_ORGANIZATION_CONSTRAINTS,
  [DIVERGENT_CONSTRAINTS_TYPE]: TASK_DIVERGENT_CONSTRAINTS,
  [TASK_INCOMING_ASSIGNMENT_REQUESTS]: INCOMING_ASSIGNMENT_REQUESTS_TYPE,
  [TASK_OUTGOING_ASSIGNMENT_REQUESTS]: OUTGOING_ASSIGNMENT_REQUESTS_TYPE,
  [TASK_EXCEEDED_POOLS]: EXCEEDED_POOLS_TYPE,
  [TASK_EXCEEDED_POOL_FORECASTS]: EXCEEDED_POOL_FORECASTS_TYPE,
  [TASK_VIOLATED_RESOURCE_CONSTRAINTS]: VIOLATED_RESOURCE_CONSTRAINTS_TYPE,
  [TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]: VIOLATED_ORGANIZATION_CONSTRAINTS_TYPE,
  [TASK_DIVERGENT_CONSTRAINTS]: DIVERGENT_CONSTRAINTS_TYPE
});

export const EVENT_LEVEL = Object.freeze({
  ALL: "ALL",
  INFO: "INFO",
  SUCCESS: "SUCCESS",
  WARNING: "WARNING",
  ERROR: "ERROR"
});

export const CLOUD_ACCOUNT_TYPE = Object.freeze({
  [AWS_CNR]: "aws",
  [AZURE_CNR]: "azure",
  [KUBERNETES_CNR]: "kubernetes",
  [ALIBABA_CNR]: "alibaba",
  [ENVIRONMENT]: "environment"
});

export const MENU_ITEM_ID = Object.freeze({
  ASSIGNMENT_RULES: "assignmentRules",
  HOME: "home",
  EXPENSES: "expenses",
  EXPENSES_MAP: "costMap",
  EXPENSES_BY_CLOUD: "expensesByCloud",
  EXPENSES_BY_POOL: "expensesByPool",
  EXPENSES_BY_OWNER: "expensesByOwner",
  ORGANIZATION: "organization",
  POOLS: "pools",
  ANOMALIES: "anomalies",
  QUOTAS_AND_BUDGETS: "quotasAndBudgets",
  TAGGING_POLICIES: "taggingPolicies",
  OPTIMIZATIONS: "recommendations",
  ARCHIVED_OPTIMIZATIONS: "archived_recommendations",
  CLOUD_HEALTH: "cloudHealth",
  K8S_RIGHTSIZING: "k8sRightsizing",
  PROJECTS: "projects",
  USER_MANAGEMENT: "userManagement",
  CLOUD_ACCOUNTS: "dataSources",
  RESOURCES: "resources",
  EVENTS: "events",
  CLOUD_MIGRATION: "cloudMigration",
  DISASTER_RECOVERY: "disasterRecovery",
  SETTINGS: "settings",
  TTL_ANALYSIS: "ttlAnalysis",
  FINOPS_PORTAL: "finOpsProtal",
  BUSINESS_INTELLIGENCE: "businessIntelligence",
  TECHNICAL_AUDIT: "technicalAudit",
  CLUSTER_TYPES: "clusterTypes",
  ENVIRONMENTS: "environments",
  INTEGRATIONS: "integrations",
  RESOURCE_LIFECYCLE: "resourceLifecycle"
});

export const MENU_SECTIONS = Object.freeze({
  FINOPS: "finops",
  OPTIMIZATION: "optimization",
  SYSTEM: "system",
  TECHNICAL_AUDIT: "technicalAudit",
  POLICIES: "policies"
});

export const DEFAULT_MAX_INPUT_LENGTH = 255;
export const NAME_MAX_SIZE = 255;
export const TAG_KEY_MAX_SIZE = 255;
export const EMAIL_MAX_LENGTH = 255;
export const MAX_ORGANIZATION_NAME_LENGTH = DEFAULT_MAX_INPUT_LENGTH;

export const ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH = 64;
export const ENVIRONMENT_PROPERTY_VALUE_MAX_INPUT_LENGTH = 2000;

export const EMPTY_UUID = "00000000-0000-0000-0000-000000000000";
export const NOT_SET_BACKEND_FILTER_VALUE = null;

export const DEFAULT_PAGE_KEY = "page";
export const DEFAULT_SEARCH_KEY = "search";

export const ONE_CENT = 0.01;

const BYTE = 1;
const KB = 1024 * BYTE;
export const MB = 1024 * KB;

export const MAX_INT_32 = 2 ** 31 - 1;
export const TTL_LIMIT_MAX = 720;

export const COMMON_YEAR_LENGTH = 365;

// Expenses filters
export const EXPENSES_LIMIT_FILTER_DEFAULT_VALUE = 5000;

export const START_DATE_BE_FILTER = "start_date";
export const START_DATE_FILTER = "startDate";

export const END_DATE_BE_FILTER = "end_date";
export const END_DATE_FILTER = "endDate";

export const CLOUD_ACCOUNT_BE_FILTER = "cloud_account";
export const CLOUD_ACCOUNT_ID_FILTER = "cloudAccountId";

export const NETWORK_TRAFFIC_FROM_BE_FILTER = "traffic_from";
export const NETWORK_TRAFFIC_FROM_FILTER = "networkTrafficFrom";

export const NETWORK_TRAFFIC_TO_BE_FILTER = "traffic_to";
export const NETWORK_TRAFFIC_TO_FILTER = "networkTrafficTo";

export const POOL_BE_FILTER = "pool";
export const POOL_ID_FILTER = "poolId";

export const OWNER_BE_FILTER = "owner";
export const OWNER_ID_FILTER = "ownerId";

export const REGION_BE_FILTER = "region";
export const REGION_FILTER = "region";

export const SERVICE_NAME_BE_FILTER = "service_name";
export const SERVICE_NAME_FILTER = "serviceName";

export const RESOURCE_TYPE_BE_FILTER = "resource_type";
export const RESOURCE_TYPE_FILTER = "resourceType";

export const ACTIVE_BE_FILTER = "active";
export const ACTIVE_FILTER = "active";

export const RECOMMENDATIONS_BE_FILTER = "recommendations";
export const AVAILABLE_SAVINGS_FILTER = "availableSavings";

export const CONSTRAINT_VIOLATED_BE_FILTER = "constraint_violated";
export const CONSTRAINT_VIOLATED_FILTER = "constraintViolated";

export const K8S_NODE_BE_FILTER = "k8s_node";
export const K8S_NODE_FILTER = "k8sNode";

export const K8S_NAMESPACE_BE_FILTER = "k8s_namespace";
export const K8S_NAMESPACE_FILTER = "k8sNamespace";

export const K8S_SERVICE_BE_FILTER = "k8s_service";
export const K8S_SERVICE_FILTER = "k8sService";

export const TAG_BE_FILTER = "tag";
export const TAG_FILTER = "tag";

export const WITHOUT_TAG_BE_FILTER = "without_tag";
export const WITHOUT_TAG_FILTER = "withoutTag";

export const ANY_NETWORK_TRAFFIC_LOCATION = "ANY";

// Optimizations
export const RECOMMENDATION_SHORT_LIVING_INSTANCES = "shortLivingInstances";
export const SHORT_LIVING_INSTANCES_TYPE = "short_living_instances";

export const RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME = "volumesNotAttachedForLongTime";
export const VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE = "volumes_not_attached_for_a_long_time";

export const RECOMMENDATION_INSTANCES_GENERATION_UPGRADE = "instancesGenerationUpgrade";
export const INSTANCES_GENERATION_UPGRADE_TYPE = "instance_generation_upgrade";

export const RECOMMENDATION_INACTIVE_USERS = "inactiveUsers";
export const INACTIVE_USERS_TYPE = "inactive_users";

export const RECOMMENDATION_INACTIVE_CONSOLE_USERS = "inactiveConsoleUsers";
export const INACTIVE_CONSOLE_USERS_TYPE = "inactive_console_users";

export const RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME = "instancesInStoppedStateForALongTime";
export const INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE = "instances_in_stopped_state_for_a_long_time";

export const RECOMMENDATION_INSTANCE_MIGRATION = "instanceMigration";
export const INSTANCE_MIGRATION_TYPE = "instance_migration";

export const RECOMMENDATION_OBSOLETE_IMAGES = "obsoleteImages";
export const OBSOLETE_IMAGES_TYPE = "obsolete_images";

export const RECOMMENDATION_OBSOLETE_SNAPSHOTS = "obsoleteSnapshots";
export const OBSOLETE_SNAPSHOTS_TYPE = "obsolete_snapshots";

export const RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS = "obsoleteSnapshotChains";
export const OBSOLETE_SNAPSHOT_CHAINS_TYPE = "obsolete_snapshot_chains";

export const RECOMMENDATION_RESERVED_INSTANCES = "reservedInstances";
export const RESERVED_INSTANCES_TYPE = "reserved_instances";

export const RECOMMENDATION_RIGHTSIZING_INSTANCES = "rightsizingInstances";
export const RIGHTSIZING_INSTANCES_TYPE = "rightsizing_instances";

export const RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES = "rightsizingRdsInstances";
export const RIGHTSIZING_RDS_INSTANCES_TYPE = "rightsizing_rds";

export const RECOMMENDATION_ABANDONED_INSTANCES = "abandonedInstances";
export const ABANDONED_INSTANCES_TYPE = "abandoned_instances";

export const RECOMMENDATION_INSTANCES_FOR_SHUTDOWN = "instancesForShutdown";
export const INSTANCES_FOR_SHUTDOWN_TYPE = "instances_for_shutdown";

export const RECOMMENDATION_INSECURE_SECURITY_GROUPS = "insecureSecurityGroups";
export const INSECURE_SECURITY_GROUPS_TYPE = "insecure_security_groups";

export const RECOMMENDATION_OBSOLETE_IPS = "obsoleteIps";
export const OBSOLETE_IPS_TYPE = "obsolete_ips";

export const RECOMMENDATION_INSTANCE_SUBSCRIPTION = "instanceSubscription";
export const INSTANCE_SUBSCRIPTION_TYPE = "instance_subscription";

export const RECOMMENDATION_ABANDONED_KINESIS_STREAMS = "abandonedKinesisStreams";
export const ABANDONED_KINESIS_STREAMS_TYPE = "abandoned_kinesis_streams";

export const RECOMMENDATION_PUBLIC_S3_BUCKETS = "publicS3Buckets";
export const PUBLIC_S3_BUCKETS_TYPE = "s3_public_buckets";

export const RECOMMENDATION_ABANDONED_S3_BUCKETS = "abandonedS3Buckets";
export const ABANDONED_S3_BUCKETS_TYPE = "s3_abandoned_buckets";

export const ACTIONABLE_RECOMMENDATIONS = Object.freeze([
  VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE,
  INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE,
  INSTANCE_MIGRATION_TYPE,
  OBSOLETE_SNAPSHOTS_TYPE,
  OBSOLETE_SNAPSHOT_CHAINS_TYPE,
  RESERVED_INSTANCES_TYPE,
  RIGHTSIZING_INSTANCES_TYPE,
  RIGHTSIZING_RDS_INSTANCES_TYPE,
  ABANDONED_INSTANCES_TYPE,
  INSTANCE_SUBSCRIPTION_TYPE,
  ABANDONED_KINESIS_STREAMS_TYPE,
  PUBLIC_S3_BUCKETS_TYPE,
  ABANDONED_S3_BUCKETS_TYPE,
  INSTANCES_GENERATION_UPGRADE_TYPE,
  INSTANCES_FOR_SHUTDOWN_TYPE
]);

export const BE_TO_FE_MAP_RECOMMENDATION_TYPES = Object.freeze({
  [SHORT_LIVING_INSTANCES_TYPE]: RECOMMENDATION_SHORT_LIVING_INSTANCES,
  [VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE]: RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
  [INACTIVE_USERS_TYPE]: RECOMMENDATION_INACTIVE_USERS,
  [INACTIVE_CONSOLE_USERS_TYPE]: RECOMMENDATION_INACTIVE_CONSOLE_USERS,
  [INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE]: RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  [INSTANCE_MIGRATION_TYPE]: RECOMMENDATION_INSTANCE_MIGRATION,
  [OBSOLETE_IMAGES_TYPE]: RECOMMENDATION_OBSOLETE_IMAGES,
  [OBSOLETE_SNAPSHOTS_TYPE]: RECOMMENDATION_OBSOLETE_SNAPSHOTS,
  [OBSOLETE_SNAPSHOT_CHAINS_TYPE]: RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
  [RESERVED_INSTANCES_TYPE]: RECOMMENDATION_RESERVED_INSTANCES,
  [RIGHTSIZING_INSTANCES_TYPE]: RECOMMENDATION_RIGHTSIZING_INSTANCES,
  [RIGHTSIZING_RDS_INSTANCES_TYPE]: RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES,
  [ABANDONED_INSTANCES_TYPE]: RECOMMENDATION_ABANDONED_INSTANCES,
  [INSTANCES_FOR_SHUTDOWN_TYPE]: RECOMMENDATION_INSTANCES_FOR_SHUTDOWN,
  [INSECURE_SECURITY_GROUPS_TYPE]: RECOMMENDATION_INSECURE_SECURITY_GROUPS,
  [OBSOLETE_IPS_TYPE]: RECOMMENDATION_OBSOLETE_IPS,
  [INSTANCE_SUBSCRIPTION_TYPE]: RECOMMENDATION_INSTANCE_SUBSCRIPTION,
  [ABANDONED_KINESIS_STREAMS_TYPE]: RECOMMENDATION_ABANDONED_KINESIS_STREAMS,
  [PUBLIC_S3_BUCKETS_TYPE]: RECOMMENDATION_PUBLIC_S3_BUCKETS,
  [ABANDONED_S3_BUCKETS_TYPE]: RECOMMENDATION_ABANDONED_S3_BUCKETS,
  [INSTANCES_GENERATION_UPGRADE_TYPE]: RECOMMENDATION_INSTANCES_GENERATION_UPGRADE
});

export const FE_TO_BE_MAP_RECOMMENDATION_TYPES = Object.freeze({
  [RECOMMENDATION_SHORT_LIVING_INSTANCES]: SHORT_LIVING_INSTANCES_TYPE,
  [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE,
  [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE,
  [RECOMMENDATION_INSTANCE_MIGRATION]: INSTANCE_MIGRATION_TYPE,
  [RECOMMENDATION_OBSOLETE_IMAGES]: OBSOLETE_IMAGES_TYPE,
  [RECOMMENDATION_OBSOLETE_SNAPSHOTS]: OBSOLETE_SNAPSHOTS_TYPE,
  [RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS]: OBSOLETE_SNAPSHOT_CHAINS_TYPE,
  [RECOMMENDATION_RESERVED_INSTANCES]: RESERVED_INSTANCES_TYPE,
  [RECOMMENDATION_RIGHTSIZING_INSTANCES]: RIGHTSIZING_INSTANCES_TYPE,
  [RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES]: RIGHTSIZING_RDS_INSTANCES_TYPE,
  [RECOMMENDATION_ABANDONED_INSTANCES]: ABANDONED_INSTANCES_TYPE,
  [RECOMMENDATION_INSTANCES_FOR_SHUTDOWN]: INSTANCES_FOR_SHUTDOWN_TYPE,
  [RECOMMENDATION_INACTIVE_USERS]: INACTIVE_USERS_TYPE,
  [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: INACTIVE_CONSOLE_USERS_TYPE,
  [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: INSECURE_SECURITY_GROUPS_TYPE,
  [RECOMMENDATION_OBSOLETE_IPS]: OBSOLETE_IPS_TYPE,
  [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: INSTANCE_SUBSCRIPTION_TYPE,
  [RECOMMENDATION_ABANDONED_KINESIS_STREAMS]: ABANDONED_KINESIS_STREAMS_TYPE,
  [RECOMMENDATION_PUBLIC_S3_BUCKETS]: PUBLIC_S3_BUCKETS_TYPE,
  [RECOMMENDATION_ABANDONED_S3_BUCKETS]: ABANDONED_S3_BUCKETS_TYPE,
  [RECOMMENDATION_INSTANCES_GENERATION_UPGRADE]: INSTANCES_GENERATION_UPGRADE_TYPE
});

export const MAP_RECOMMENDATION_TYPES = Object.freeze({
  ...BE_TO_FE_MAP_RECOMMENDATION_TYPES,
  ...FE_TO_BE_MAP_RECOMMENDATION_TYPES
});

export const RECOMMENDATIONS_LIMIT_FILTER = 100;

export const RECOMMENDATIONS_TABS = Object.freeze({
  ACTIVE: "active",
  DISMISSED: "dismissed",
  EXCLUDED: "excluded"
});

// AWS Root account connection schemes
export const AWS_ROOT_CONNECT_CONFIG_SCHEMES = Object.freeze({
  FIND_REPORT: "find_report",
  CREATE_REPORT: "create_report",
  BUCKET_ONLY: "bucket_only"
});

export const SUMMARY_VALUE_COMPONENT_TYPES = Object.freeze({
  FormattedNumber: "FormattedNumber",
  FormattedMoney: "FormattedMoney",
  FormattedMessage: "FormattedMessage",
  Custom: "Custom"
});

export const SUMMARY_CARD_TYPES = Object.freeze({
  BASIC: "basic",
  EXTENDED: "extended"
});

export const SCOPE_TYPES = Object.freeze({
  ORGANIZATION: "organization",
  POOL: "pool",
  RESOURCE: "resource"
});

export const BEST_OVERALL_REGION = "best_overall_region";
export const RUNNER_UP_REGION = "runner_up_region";
export const CHEAPEST_FROM_TOP_FIVE_REGION = "cheapest_top_five_region";
export const BEST_AVAILABILITY_ZONE = "best_az";
export const BEST_AVAILABILITY_ZONE_FOR_SPOT = "best_az_for_spot";

// Currently not provided by the API
export const BEST_FOR_NEW_WORKLOADS = "best_for_new_workloads";
export const BEST_FOR_EXISTING_WORKLOADS_SCALING = "best_for_existing_workloads_scaling";
export const BEST_FOR_SPOT = "best_for_spot";

export const CLOUD_HEALTH_TYPES = Object.freeze({
  [BEST_OVERALL_REGION]: "bestOverallScoredRegion",
  [RUNNER_UP_REGION]: "runnerUpRegion",
  [CHEAPEST_FROM_TOP_FIVE_REGION]: "cheapestRegionFromTopFive",
  [BEST_AVAILABILITY_ZONE]: "bestScoredAvailabilityZone",
  [BEST_AVAILABILITY_ZONE_FOR_SPOT]: "bestAvailabilityZoneForSpotInstances",
  [BEST_FOR_NEW_WORKLOADS]: "bestForNewWorkLoads",
  [BEST_FOR_EXISTING_WORKLOADS_SCALING]: "bestForExistingWorkLoadsScaling",
  [BEST_FOR_SPOT]: "bestForSpotInstances"
});

export const CLOUD_HEALTH_SCORES = Object.freeze({
  BASE_BOTTOM_LOW_LIMIT: 3,
  BASE_BOTTOM_MEDIUM_LIMIT: 7,
  PRICE: Object.freeze({
    INDEPENDENT_COMPUTE: 8,
    DATA_STORAGE: 7,
    NEW_WORKLOADS: 8
  }),
  PROXIMITY: Object.freeze({
    COMPUTE_SCALING: 8,
    DATA_STORAGE: 7,
    EXISTING_WORKLOADS: 8,
    HOME_REGION: 9
  }),
  NETWORK_LATENCY: Object.freeze({
    COMPUTE_SCALING: 9,
    EXISTING_WORKLOADS: 9
  }),
  CAPACITY: Object.freeze({
    SPOT_INSTANCES: 9
  })
});

export const CLOUD_HEALTH_DOMESTIC_REGIONS = Object.freeze({
  AWS_US: Object.freeze(["us-east-1", "us-east-2", "us-west-1", "us-west-2"]),
  AWS_EU: Object.freeze(["eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-south-1", "eu-north-1"]),
  AZURE_US: Object.freeze([
    "westcentralus",
    "southcentralus",
    "usseceast",
    "usdodeast",
    "northcentralus",
    "westus",
    "ussecwest",
    "eastus2",
    "westus2",
    "centralus",
    "usdodcentral",
    "eastus"
  ]),
  AZURE_EU: Object.freeze([
    "germanycentral",
    "switzerlandwest",
    "germanynortheast",
    "francecentral",
    "germanynorth",
    "switzerlandnorth",
    "westeurope",
    "norwaywest",
    "norwayeast",
    "germanywestcentral",
    "francesouth",
    "northeurope"
  ])
});

export const START_DATE_PICKER_NAME = "startDate";
export const END_DATE_PICKER_NAME = "endDate";

export const PDF_ELEMENTS = Object.freeze({
  // reactive components with PDFAble child
  costExplorer: Object.freeze({
    dates: "costExplorerDates",
    expensesSummary: "costExplorerExpensesSummary",
    previousExpensesSummary: "costExplorerPreviousExpensesSummary",
    barChart: "costExplorerBarChart",
    periodWidgetTitle: "costExplorerPeriodWidgetTitle"
  }),

  // elements with "inline renders" inside download button click handler
  basics: Object.freeze({
    H1: "basic elements h1",
    H2: "basic elements h2",
    fileName: "set file name"
  }),

  // types for static pdf markup stuff, no reactive data inside
  markup: Object.freeze({
    initLandscape: "inits landscape doc",
    initPortrait: "inits portrait doc",
    newPortraitPage: "new portrait page",
    newLandscapePage: "new landscape page",
    logo: "optscale logotype",
    spacer: "vertical spacer",
    footer: "footer copyright"
  })
});

// TTL Analysis
export const TTL_MODES = Object.freeze({
  PREDEFINED_TTL: "predefined",
  CUSTOM_TTL: "custom"
});

export const TTL_ANALYSIS_QUERY_PARAMETERS = Object.freeze({
  POOL_ID: "poolId",
  TTL: "ttl"
});

export const TTL_ANALYSIS_TOP_SECTION_TYPES = Object.freeze({
  FORM: "form",
  APPLIED_FILTERS: "appliedFilters"
});

export const TTL_ANALYSIS_FORM_FIELD_NAMES = Object.freeze({
  POOL_ID: "poolId",
  TTL_MODE: "ttlMode"
});

export const TAB_QUERY_PARAM_NAME = "tab";

// Resource details page
export const RESOURCE_PAGE_TABS = Object.freeze({
  DETAILS: "details",
  SUB_RESOURCES: "subResources",
  CONSTRAINTS: "constraints",
  EXPENSES: "expenses",
  RECOMMENDATIONS: "recommendations",
  MONITORING: "monitoring",
  COST_MODEL: "costModel",
  BOOKINGS: "bookings"
});

// Cloud account details page
export const CLOUD_ACCOUNT_DETAILS_PAGE_TABS = Object.freeze({
  DETAILS: "details",
  UPLOAD: "upload",
  NODES: "nodes"
});
// Resource page expenses tab
export const RESOURCE_PAGE_EXPENSES_TABS = Object.freeze({
  GROUPED: "grouped",
  DETAILED: "detailed",
  PAID_NETWORK_TRAFFIC: "paidNetworkTraffic"
});

export const DATE_RANGE_FILTERS = Object.freeze({
  ALL: "all",
  LAST_WEEK: "lastWeek",
  THIS_WEEK: "thisWeek",
  LAST_MONTH: "lastMonth",
  THIS_MONTH: "thisMonth"
});

export const RESOURCE_PAGE_TAB_QUERY_PARAM_NAME = "tab";

export const LINEAR_SELECTOR_ITEMS_TYPES = Object.freeze({
  TEXT: "text",
  POPOVER: "popover",
  MULTISELECT_POPOVER: "multiSelectPopover"
});

export const RESOURCE_VISIBILITY_ACTIONS = {
  DISMISS: "dismiss",
  ACTIVATE: "activate"
};

export const RESOURCE_VISIBILITY_STATUSES = {
  ACTIVE: "active",
  DISMISSED: "dismissed",
  EXCLUDED: "excluded"
};

export const FORMATTED_MONEY_TYPES = Object.freeze({
  COMMON: "common",
  COMPACT: "compact",
  TINY: "tiny",
  TINY_COMPACT: "tinyCompact"
});

export const ORGANIZATION_OVERVIEW_TABS = Object.freeze({
  POOLS: "pools",
  ASSIGNMENT_RULES: "assignmentRules",
  CONSTRAINTS: "constraints"
});

export const ORGANIZATIONS_OVERVIEW_FILTERS = Object.freeze({
  ALL: "all",
  REQUIRING_ATTENTION: "requiringAttention",
  ALL_FINE: "allFine"
});

export const ENVIRONMENTS_STATUS_FILTERS = Object.freeze({
  ALL: "all",
  AVAILABLE: "available",
  UNAVAILABLE: "unavailable",
  IN_USE: "inUse"
});

export const ENVIRONMENTS_ACCESS_FILTERS = Object.freeze({
  ALL: "all",
  GRANTED: "granted",
  RESTRICTED: "restricted"
});

export const LOGO_SIZE = Object.freeze({
  FULL: "full",
  SHORT: "short"
});

export const WEEK_LENGTH = 7;

export const EXPENSES_BREAKDOWN_PERIODS = Object.freeze({
  DAILY: "daily",
  WEEKLY: "weekly",
  MONTHLY: "monthly"
});

export const DATE_RANGE_TYPE = Object.freeze({
  EXPENSES: "expenses",
  RESOURCES: "resources",
  TTL_ANALYSIS: "ttlAnalysis",
  ARCHIVED_RECOMMENDATIONS: "archivedRecommendations"
});

export const METRIC_TYPES = Object.freeze({
  CPU: "cpu",
  MEMORY: "memory",
  DISK_IO: "disk_io",
  NETWORK: "network"
});

export const COST_MODEL_TYPES = Object.freeze({
  K8S: "k8s",
  ENVIRONMENT: "environment"
});

export const OPTSCALE_RESOURCE_TYPES = Object.freeze({
  CLUSTER: "cluster",
  ENVIRONMENT: "environment",
  REGULAR: "regular"
});

export const COST_MODEL_MONEY_MAXIMUM_FRACTION_DIGITS = 6;

export const CLEAN_EXPENSES_GROUP_TYPES = Object.freeze({
  POOL: "pool",
  OWNER: "owner",
  TAG: "tag"
});

export const ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER = "conditions";

export const ALERT_SEVERITY = Object.freeze({
  ERROR: "error",
  INFO: "info",
  SUCCESS: "success",
  WARNING: "warning"
});

export const INFINITY_SIGN = "∞";

export const RECOMMENDATION_CATEGORY_QUERY_PARAMETER = "category";
export const RECOMMENDATION_TYPE_QUERY_PARAMETER = "recommendation";

export const ENVIRONMENT_SOFTWARE_FIELD = "Software ";
export const ENVIRONMENT_JIRA_TICKETS_FIELD = "Jira tickets ";
export const ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS = Object.freeze({
  [ENVIRONMENT_SOFTWARE_FIELD]: "environmentsSoftware",
  [ENVIRONMENT_JIRA_TICKETS_FIELD]: "environmentsJiraTickets"
});

export const DOWNLOAD_FILE_FORMATS = Object.freeze({
  JSON: "json",
  XLSX: "xlsx"
});

export const ENV_COLLECTOR_URL = "ENV_COLLECTOR_URL";

export const DEFAULT_BAR_CHART_HEIGHT = 40;

export const DEFAULT_BAR_CHART_PADDING = 0.7;

export const DEFAULT_BAR_CHART_INNER_PADDING = 0;

export const DEFAULT_BAR_CHART_MARGIN = Object.freeze({
  top: 20,
  bottom: 50,
  right: 50,
  left: 75
});

export const RESOURCE_LIMIT_HIT_STATE = Object.freeze({
  RED: "red",
  GREEN: "green"
});

export const CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX = "expenses";

export const PROVIDE_DATA_STEPS = Object.freeze({
  PLAN: "plan",
  INFRASTRUCTURE: "infrastructure",
  CODE: "code",
  SURVEY: "survey",
  REVIEW_AND_SUBMIT: "reviewAndSubmit"
});

export const DEFAULT_CHART_BORDER_WIDTH = 0;

export const GANALYTICS_ID = "UA-82924850-6";

export const RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY = Object.freeze({
  EMPLOYEE_ID: "employee_id",
  POOL_ID: "pool_id",
  CLOUD_ACCOUNT_ID: "cloud_account_id",
  SERVICE_NAME: "service_name",
  REGION: "region",
  RESOURCE_TYPE: "resource_type",
  K8S_NODE: "k8s_node",
  K8S_NAMESPACE: "k8s_namespace",
  K8S_SERVICE: "k8s_service"
});

export const RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES = Object.freeze(Object.values(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY));

export const RESOURCE_COUNT_ANOMALY = "resource_count_anomaly";

export const EXPENSE_ANOMALY = "expense_anomaly";
export const ANOMALY_TYPES = Object.freeze({
  [RESOURCE_COUNT_ANOMALY]: "resourceCount",
  [EXPENSE_ANOMALY]: "expenses"
});

export const QUOTA_POLICY = "resource_quota";
export const RECURRING_BUDGET_POLICY = "recurring_budget";
export const EXPIRING_BUDGET_POLICY = "expiring_budget";
export const QUOTAS_AND_BUDGETS_TYPES = Object.freeze({
  [QUOTA_POLICY]: "resourceQuota",
  [RECURRING_BUDGET_POLICY]: "recurringBudget",
  [EXPIRING_BUDGET_POLICY]: "expiringBudget"
});

export const TAGGING_POLICY = "tagging_policy";
export const TAGGING_POLICY_TYPES = Object.freeze({
  [TAGGING_POLICY]: "taggingPolicy"
});

export const POLICY_TYPE_COLUMN_NAMES = Object.freeze({
  [RESOURCE_COUNT_ANOMALY]: "resourceCountColumnName",
  [EXPENSE_ANOMALY]: "expensesColumnName",
  [QUOTA_POLICY]: "resourceQuotaColumnName",
  [RECURRING_BUDGET_POLICY]: "recurringBudgetColumnName",
  [EXPIRING_BUDGET_POLICY]: "expiringBudgetColumnName",
  [TAGGING_POLICY]: "taggingPolicyColumnName"
});

export const RIGHTSIZING_METRIC_LIMIT_TYPES = Object.freeze({
  Q99: "qtl99",
  MAX: "max",
  AVG: "avg"
});

export const METADATA_FIELDS = Object.freeze({
  FIRST_SEEN: "metadata.firstSeen",
  LAST_SEEN: "metadata.lastSeen",
  IMAGE_ID: "metadata.imageId",
  OS: "metadata.os",
  PREINSTALLED: "metadata.preinstalled",
  FLAVOR: "metadata.flavor",
  CPU_COUNT: "metadata.cpuCount",
  STATE: "metadata.state",
  ZONE_ID: "metadata.zoneId",
  SNAPSHOT_ID: "metadata.snapshotId",
  SIZE: "metadata.size",
  VOLUME_ID: "metadata.volumeId",
  ENGINE_VERSION: "metadata.engineVersion",
  ENGINE: "metadata.engine",
  VOLUME_TYPE: "metadata.volumeType",
  STORAGE_TYPE: "metadata.storageType",
  ATTACHED: "metadata.attached",
  LAST_ATTACHED: "metadata.lastAttached",
  LAST_USED: "metadata.lastUsed",
  HOST_IP: "metadata.hostIp",
  CATEGORY: "metadata.category",
  POD_IP: "metadata.podIp",
  VPC_ID: "metadata.vpcId",
  VPC_NAME: "metadata.vpcName"
});

export const INSECURE_PORTS_MAP = Object.freeze({
  20: "FTP",
  21: "FTP",
  22: "SSH",
  23: "Telnet",
  25: "SMTP",
  43: "WHOIS",
  53: "DNS",
  80: "HTTP",
  123: "NTP",
  143: "IMAP",
  389: "LDAP",
  443: "HTTPS",
  465: "SMTP over TLS",
  853: "DNS over TLS",
  944: "NFS",
  989: "FTPS (FTP over SSL)",
  990: "FTPS (FTP over SSL)",
  992: "Telnet",
  993: "IMAPS (IMAP over SSL)",
  1433: "SQL Server (MSSQL)",
  1434: "SQL Server (MSSQL)",
  1521: "Oracle DB",
  1830: "Oracle DB",
  2181: "ZooKeeper",
  2379: "etcd",
  2380: "etcd",
  2888: "ZooKeeper",
  3306: "MySQL",
  3389: "RDP",
  3888: "ZooKeeper",
  5432: "PostgreSQL",
  5050: "Mesos",
  5051: "Mesos",
  5984: "CouchDB",
  6379: "Redis",
  6443: "Kubernetes",
  7000: "Cassandra",
  7001: "Cassandra",
  7210: "MaxDB",
  7473: "Neo4J",
  7474: "Neo4J",
  8087: "Riak",
  8098: "Riak",
  8529: "ArangoDB",
  9042: "Cassandra",
  9200: "Elasticsearch",
  9300: "Elasticsearch",
  11211: "Memcached",
  15672: "RabbitMQ Web UI",
  27017: "MongoDB",
  27018: "MongoDB",
  27019: "MongoDB",
  28015: "RethinkDB",
  28017: "MongoDB",
  29015: "RethinkDB"
});

export const MIN_PORT = 0;

export const MAX_PORT = 65535;

export const EXPENSES_MAP_TYPES = Object.freeze({
  REGION: "region",
  TRAFFIC: "networkTraffic"
});

export const EXPENSES_MAP_OBJECT_TYPES = Object.freeze({
  LOCATION: "location",
  FLOW: "flow",
  EXTERNAL_MARKER: "externalMarker",
  INTER_REGION_MARKER: "interRegionMarker"
});

export const ARCHIVATION_REASON_MESSAGE_ID = Object.freeze({
  options_changed: "archivationReason.optionsHaveBeenChanged",
  cloud_account_deleted: "archivationReason.dataSourceHasBeenDeleted",
  resource_deleted: "archivationReason.resourceHasBeenDeleted",
  recommendation_applied: "archivationReason.recommendationHasBeenApplied",
  recommendation_irrelevant: "archivationReason.recommendationHasBecomeIrrelevant",
  failed_dependency: "archivationReason.dataSourceSettingsHaveBeenUpdated"
});

export const ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID = Object.freeze({
  options_changed: "archivationReason.optionsHaveBeenChanged.description",
  cloud_account_deleted: "archivationReason.dataSourceHasBeenDeleted.description",
  resource_deleted: "archivationReason.resourceHasBeenDeleted.description",
  recommendation_applied: "archivationReason.recommendationHasBeenApplied.description",
  recommendation_irrelevant: "archivationReason.recommendationHasBecomeIrrelevant.description",
  failed_dependency: "archivationReason.dataSourceSettingsHaveBeenUpdated.description"
});
