import { NIL as NIL_UUID } from "uuid";

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

export const POOL_TYPES_LIST = Object.freeze(Object.keys(POOL_TYPES));

// Data Sources
export const AWS_CNR = "aws_cnr";
export const AZURE_CNR = "azure_cnr";
export const AZURE_TENANT = "azure_tenant";
export const GCP_CNR = "gcp_cnr";
export const KUBERNETES_CNR = "kubernetes_cnr";
export const ALIBABA_CNR = "alibaba_cnr";
export const NEBIUS = "nebius";
export const ENVIRONMENT = "environment";

export const DATA_SOURCE_TYPES = [AWS_CNR, AZURE_CNR, GCP_CNR, KUBERNETES_CNR, ALIBABA_CNR, NEBIUS, ENVIRONMENT];

export const AWS_ROOT_ACCOUNT = "awsRoot";
export const AWS_LINKED_ACCOUNT = "awsLinked";
export const AZURE_SUBSCRIPTION = "azureSubscription";
export const AZURE_TENANT_ACCOUNT = "azureTenant";
export const KUBERNETES = "kubernetes";
export const ALIBABA_ACCOUNT = "alibaba";
export const GCP_ACCOUNT = "gcp";
export const NEBIUS_ACCOUNT = "nebius";

export const DATASOURCE_TYPE = "type";

export const NOT_SET_CLOUD_TYPE = "not_set";

export const CLOUD_ACCOUNT_TYPE = Object.freeze({
  [AWS_CNR]: "aws",
  [AZURE_CNR]: "azureSubscription",
  [AZURE_TENANT]: "azureTenant",
  [KUBERNETES_CNR]: "kubernetes",
  [ALIBABA_CNR]: "alibaba",
  [GCP_CNR]: "gcp",
  [ENVIRONMENT]: "environment",
  [NEBIUS]: "nebius"
});

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

export const EVENT_LEVEL = Object.freeze({
  // The events API doesn't support the "ALL" level string, so we need to use the "undefined" in order to get a list of all events
  ALL: undefined,
  INFO: "INFO",
  WARNING: "WARNING",
  ERROR: "ERROR"
});

export const CLOUD_ACCOUNT_TYPES_LIST = Object.keys(CLOUD_ACCOUNT_TYPE);

export const DEFAULT_MAX_INPUT_LENGTH = 255;
export const NAME_MAX_SIZE = 255;
export const TAG_KEY_MAX_SIZE = 255;
export const EMAIL_MAX_LENGTH = 255;
export const MAX_ORGANIZATION_NAME_LENGTH = DEFAULT_MAX_INPUT_LENGTH;

export const ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH = 64;
export const ENVIRONMENT_PROPERTY_VALUE_MAX_INPUT_LENGTH = 2000;

export const EMPTY_UUID = NIL_UUID;
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

export const STATUS_BE_FILTER = "status";
export const STATUS_FILTER = "status";

export const GOALS_BE_FILTER = "goals";
export const GOALS_FILTER = "goals";

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
export const RECOMMENDATIONS_LIMIT_FILTER = 100;

export const SETTINGS_TYPE_SUCCESS_MESSAGE = Object.freeze({
  THRESHOLDS: "thresholds",
  RIGHTSIZING_STRATEGY: "rightsizingStrategy",
  EXCLUSIONS: "exclusions",
  INSECURE_PORTS: "insecurePorts"
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
  ADVANCED: "advanced",
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
  MULTISELECT_POPOVER: "multiSelectPopover",
  RANGE: "range"
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
  ALL: "anyStatus",
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

export const EXPENSES_SPLIT_PERIODS = Object.freeze({
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

export const CLEAN_EXPENSES_GROUP_TYPES_LIST = Object.values(CLEAN_EXPENSES_GROUP_TYPES);

export const ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER = "conditions";

export const ALERT_SEVERITY = Object.freeze({
  ERROR: "error",
  INFO: "info",
  SUCCESS: "success",
  WARNING: "warning"
});

export const INFINITY_SIGN = "∞";

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

export const GOAL_STATUS = Object.freeze({
  MET: "goalMet",
  NOT_MET: "goalNotMet"
});

export const GOALS_FILTER_TYPES = Object.freeze({
  LESS_IS_BETTER: "less",
  MORE_IS_BETTER: "more"
});

export const AGGREGATE_FUNCTIONS = Object.freeze({
  LAST: "last",
  SUM: "sum",
  MAX: "max",
  AVERAGE: "average"
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

export const ML_EXECUTORS_DAILY_BREAKDOWN_BY = Object.freeze({
  CPU: "cpu",
  RAM: "ram",
  EXECUTORS_COUNT: "executors_count",
  PROCESS_CPU: "process_cpu",
  PROCESS_RAM: "process_ram",
  GPU_LOAD: "gpu_load",
  GPU_MEMORY_USED: "gpu_memory_used"
});

export const ML_EXECUTORS_BREAKDOWN_BY_MESSAGES = Object.freeze({
  CPU: "cpu",
  RAM: "ram",
  EXECUTORS_COUNT: "executorsCount",
  PROCESS_CPU: "processCPU",
  PROCESS_RAM: "processRAM",
  GPU_LOAD: "gpu",
  GPU_MEMORY_USED: "gpuMemory"
});

export const ML_MODEL_RUN_DAILY_BREAKDOWN_BY_VALUES = Object.freeze(Object.values(ML_EXECUTORS_DAILY_BREAKDOWN_BY));

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
  VPC_NAME: "metadata.vpcName",
  PAYMENT_OPTION: "metadata.paymentOption",
  OFFERING_TYPE: "metadata.offeringType",
  PURCHASE_TERM: "metadata.purchaseTerm",
  APPLIED_REGION: "metadata.appliedRegion",
  FOLDER_ID: "metadata.folderId",
  SOURCE_CLUSTER_ID: "metadata.sourceClusterId",
  PLATFORM_NAME: "metadata.platformName",
  RAM: "metadata.ram",
  PLATFORM_ID: "metadata.platformId"
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

export const CLEAN_EXPENSES_BREAKDOWN_TYPES = Object.freeze({
  EXPENSES: "expenses",
  RESOURCE_COUNT: "resourceCount",
  TAGS: "tags"
});

export const CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST = Object.values(CLEAN_EXPENSES_BREAKDOWN_TYPES);

// TODO: add render here to the definitions
// value is obsolete
export const BREAKDOWN_LINEAR_SELECTOR_ITEMS = [
  {
    name: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
    value: "expenses",
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_expenses"
  },
  {
    name: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
    value: "resource_type",
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_resource_count"
  },
  {
    name: CLEAN_EXPENSES_BREAKDOWN_TYPES.TAGS,
    value: "tags",
    type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
    dataTestId: "breakdown_ls_item_tags"
  }
];

export const ML_MODEL_DETAILS_TABS = Object.freeze({
  OVERVIEW: "overview",
  EXECUTORS: "executors"
});

export const ML_RUN_STATUS = Object.freeze({
  STOPPED: "stopped",
  ABORTED: "aborted",
  COMPLETED: "completed",
  RUNNING: "running",
  FAILED: "failed"
});

export const ML_MODEL_STATUS = Object.freeze({
  CREATED: "created",
  ABORTED: "aborted",
  COMPLETED: "completed",
  RUNNING: "running",
  FAILED: "failed"
});

export const TENDENCY = Object.freeze({
  MORE: "more",
  LESS: "less"
});

export const SORTING_ORDER = Object.freeze({
  ASC: "asc",
  DESC: "desc"
});

export const FREE_ACCOUNT_30_DAYS_EXPENSES_THRESHOLD = 30000;

/**
 * https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
 * Only regions with not required opt-in-status
 */
export const RUNSET_TEMPLATE_REGIONS = Object.freeze([
  { id: "us-east-1", name: "us-east-1", cloudType: AWS_CNR },
  { id: "us-east-2", name: "us-east-2", cloudType: AWS_CNR },
  { id: "us-west-1", name: "us-west-1", cloudType: AWS_CNR },
  { id: "us-west-2", name: "us-west-2", cloudType: AWS_CNR },
  { id: "ap-south-1", name: "ap-south-1", cloudType: AWS_CNR },
  { id: "ap-southeast-1", name: "ap-southeast-1", cloudType: AWS_CNR },
  { id: "ap-southeast-2", name: "ap-southeast-2", cloudType: AWS_CNR },
  { id: "ap-northeast-1", name: "ap-northeast-1", cloudType: AWS_CNR },
  { id: "ap-northeast-2", name: "ap-northeast-2", cloudType: AWS_CNR },
  { id: "ap-northeast-3", name: "ap-northeast-3", cloudType: AWS_CNR },
  { id: "ca-central-1", name: "ca-central-1", cloudType: AWS_CNR },
  { id: "eu-central-1", name: "eu-central-1", cloudType: AWS_CNR },
  { id: "eu-west-1", name: "eu-west-1", cloudType: AWS_CNR },
  { id: "eu-west-2", name: "eu-west-2", cloudType: AWS_CNR },
  { id: "eu-west-3", name: "eu-west-3", cloudType: AWS_CNR },
  { id: "eu-north-1", name: "eu-north-1", cloudType: AWS_CNR },
  { id: "sa-east-1", name: "sa-east-1", cloudType: AWS_CNR }
]);

export const RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE = Object.freeze({
  ACCELERATED_COMPUTING: "accelerated_computing",
  GENERAL_PURPOSE: "general_purpose",
  COMPUTE_OPTIMIZED: "compute_optimized",
  MEMORY_OPTIMIZED: "memory_optimized",
  STORAGE_OPTIMIZED: "storage_optimized",
  HPC_OPTIMIZED: "hpc_optimized"
});

// https://aws.amazon.com/ec2/instance-types/
export const RUNSET_TEMPLATE_INSTANCE_TYPES = Object.freeze([
  { name: "p4", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "p3", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "p2", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "dL1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "trn1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "inf2", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "inf1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "g5", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "g5g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "g4dn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "g4ad", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "g3", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "f1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },
  { name: "vt1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING },

  { name: "m7g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "mac", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m6g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m6i", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m6in", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m6a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m5", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m5n", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m5zn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m5a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "m4", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "a1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "t4g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "t3", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "t3a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },
  { name: "t2", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.GENERAL_PURPOSE },

  { name: "c7g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c7gn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c6i", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c6in", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c6a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c6g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c6gn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c5", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c5n", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c5a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },
  { name: "c4", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.COMPUTE_OPTIMIZED },

  { name: "r7g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "r7iz", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "r6g", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R6i", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R6a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R5", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R5n", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R5b", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R5a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "R4", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X2gd", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X2idn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X2iedn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X2iezn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "X1e", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "High Memory", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },
  { name: "z1d", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.MEMORY_OPTIMIZED },

  { name: "im4gn", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "is4gen", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "i4i", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "i3", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "i3en", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "d2", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "d3", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "d3en", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },
  { name: "h1", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.STORAGE_OPTIMIZED },

  { name: "hpc6id", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.HPC_OPTIMIZED },
  { name: "hpc6a", cloudType: AWS_CNR, type: RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.HPC_OPTIMIZED }
]);

export const ML_RUNSET_ABORT_CONDITION_TYPES = Object.freeze({
  MAX_BUDGET: "max_budget",
  REACHED_GOALS: "reached_goals",
  MAX_DURATION: "max_duration"
});
