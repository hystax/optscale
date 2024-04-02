import {
  ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER,
  EXPENSES_FILTERBY_TYPES,
  POOL_ID_FILTER,
  RESOURCE_TYPE_FILTER,
  START_DATE_FILTER,
  END_DATE_FILTER,
  TAB_QUERY_PARAM_NAME,
  EMPTY_UUID,
  KUBERNETES,
  DATASOURCE_TYPE
} from "utils/constants";
import { getLast30DaysRange, getCurrentMonthRange } from "utils/datetime";
import { formQueryString } from "utils/network";

import { buildQueryParameters, concatenateUrl, hasSymbolAtTheEnd, isString } from "utils/strings";

const CREATE = "create";
const CONNECT = "connect";
const INVITE = "invite";
const EDIT = "edit";

export const getDocsFileUrl = (url: string) =>
  `/docs/${(url === "/" ? "home" : url)
    .replace(/:.*?(\/|$)/g, "id/") // replace dynamic ID segments (:poolId/) with just id (id/)
    .replace(/(\/$|^\/)/g, "") // remove leading and trailing slash from a string
    .replace(/\//g, "-")}.md`; // replace slashes with -

export const HOME = "/";
export const getHomeUrl = (organizationId) =>
  organizationId ? concatenateUrl([HOME, `?organizationId=${organizationId}`], "", "") : HOME;
export const SHOW_POLICY_QUERY_PARAM = "showPolicy";
export const HOME_FIRST_TIME = `/?${SHOW_POLICY_QUERY_PARAM}=true`;
export const LOGIN = "/login";
export const REGISTER = "/register";
export const INVITED = "/invited";
export const RESET_PASSWORD = "/reset-password";
export const ACCEPT_INVITATION = "/accept-invitation";
export const ACCEPT_INVITATIONS = "/accept-invitations";

export const POOL_BASE = "pool";
export const POOLS_BASE = "pools";
const POOL_IDENTIFIER = ":poolId";

export const USER_MANAGEMENT_BASE_URL = "users";
const EMPLOYEE_IDENTIFIER = ":employeeId";

export const CLOUD_ACCOUNT_BASE_URL = "cloud-account";
const CLOUD_ACCOUNTS_BASE_URL = "cloud-accounts";
const CLOUD_ACCOUNT_IDENTIFIER = ":cloudAccountId";

const RESOURCE_IDENTIFIER = ":resourceId";

// FinOps
const EXPENSES_BASE = "expenses";
export const CLOUD_EXPENSES_BASE = "cloud-expenses";
export const POOL_EXPENSES_BASE = "pool-expenses";
export const OWNER_EXPENSES_BASE = "owner-expenses";
export const EXPENSES_MAP_BASE = "expenses-map";

export const EXPENSES = concatenateUrl([EXPENSES_BASE]);
export const EXPENSES_MAP = concatenateUrl([EXPENSES_MAP_BASE]);

export const EXPENSES_BY_CLOUD = concatenateUrl([EXPENSES_BASE, `?filterBy=${EXPENSES_FILTERBY_TYPES.CLOUD}`], "/", "");
export const CLOUD_EXPENSES = concatenateUrl([CLOUD_EXPENSES_BASE, CLOUD_ACCOUNT_IDENTIFIER]);
export const getCloudExpensesUrl = (cloudAccountId) => CLOUD_EXPENSES.replace(CLOUD_ACCOUNT_IDENTIFIER, cloudAccountId);

export const EXPENSES_BY_POOL = concatenateUrl([EXPENSES_BASE, `?filterBy=${EXPENSES_FILTERBY_TYPES.POOL}`], "/", "");
export const POOL_EXPENSES = concatenateUrl([POOL_EXPENSES_BASE, POOL_IDENTIFIER]);

export const FINOPS_PORTAL = "/finops-portal";

// BI
export const BUSINESS_INTELLIGENCE = "/business-intelligence";
const BI_EXPORTS_BASE = "bi-exports";
const BI_EXPORTS_IDENTIFIER = ":biExportId";

export const BI_EXPORTS = concatenateUrl([BI_EXPORTS_BASE]);
export const BI_EXPORT = concatenateUrl([BI_EXPORTS_BASE, BI_EXPORTS_IDENTIFIER]);
export const CREATE_BI_EXPORT = concatenateUrl([BI_EXPORTS_BASE, CREATE]);
export const EDIT_BI_EXPORT = concatenateUrl([BI_EXPORTS_BASE, BI_EXPORTS_IDENTIFIER, EDIT]);

export const getBIExportUrl = (biExportId) => BI_EXPORT.replace(BI_EXPORTS_IDENTIFIER, biExportId);
export const getEditBIExportUrl = (biExportId) => EDIT_BI_EXPORT.replace(BI_EXPORTS_IDENTIFIER, biExportId);

// We should also check if we can generalize other get[Enitity]ExpensesUrl
export const getPoolExpensesUrl = (poolId) => POOL_EXPENSES.replace(POOL_IDENTIFIER, poolId);
export const getThisMonthPoolExpensesUrl = (poolId) => {
  const { today, startOfMonth } = getCurrentMonthRange(true);
  return `${getPoolExpensesUrl(poolId)}?startDate=${startOfMonth}&endDate=${today}&filterBy=${EXPENSES_FILTERBY_TYPES.POOL}`;
};

export const EXPENSES_BY_OWNER = concatenateUrl([EXPENSES_BASE, `?filterBy=${EXPENSES_FILTERBY_TYPES.EMPLOYEE}`], "/", "");
export const OWNER_EXPENSES = concatenateUrl([OWNER_EXPENSES_BASE, EMPLOYEE_IDENTIFIER]);
export const getOwnerExpensesUrl = (employeeId) => OWNER_EXPENSES.replace(EMPLOYEE_IDENTIFIER, employeeId);

// Pools
export const POOLS = concatenateUrl([POOLS_BASE]);
export const POOL_QUERY_PARAM_NAME = "pool";
export const EDIT_POOL_TAB_QUERY = "poolEditTab";
export const getPoolUrl = (poolId) => concatenateUrl([POOLS, `${POOL_QUERY_PARAM_NAME}=${poolId}`], "", "?");

export const WITH_SUBPOOLS_SIGN = "+";
export const getPoolIdWithSubPools = (id) => `${id}${id !== EMPTY_UUID ? WITH_SUBPOOLS_SIGN : ""}`;
export const getPoolIdWithSubPoolsEncoded = (id) => encodeURIComponent(getPoolIdWithSubPools(id));
export const isPoolIdWithSubPools = (poolId) => (isString(poolId) ? hasSymbolAtTheEnd(poolId, WITH_SUBPOOLS_SIGN) : false);

// Anomalies
export const ANOMALIES_BASE = "anomalies";
const ANOMALY_IDENTIFIER = ":anomalyId";

export const ANOMALIES = concatenateUrl([ANOMALIES_BASE]);
export const ANOMALY = concatenateUrl([ANOMALIES_BASE, ANOMALY_IDENTIFIER]);
export const getAnomalyUrl = (anomalyId) => ANOMALY.replace(ANOMALY_IDENTIFIER, anomalyId);

export const ANOMALY_CREATE = concatenateUrl([ANOMALIES_BASE, CREATE]);

// Quotas and budgets
export const QUOTAS_AND_BUDGETS_BASE = "policies";
const QUOTA_AND_BUDGET_IDENTIFIER = ":policyId";

export const QUOTAS_AND_BUDGETS = concatenateUrl([QUOTAS_AND_BUDGETS_BASE]);
export const QUOTA_AND_BUDGET = concatenateUrl([QUOTAS_AND_BUDGETS_BASE, QUOTA_AND_BUDGET_IDENTIFIER]);
export const getQuotaAndBudgetUrl = (policyId) => QUOTA_AND_BUDGET.replace(QUOTA_AND_BUDGET_IDENTIFIER, policyId);

export const QUOTA_AND_BUDGET_CREATE = concatenateUrl([QUOTAS_AND_BUDGETS_BASE, CREATE]);

// Tagging policies
export const TAGGING_POLICIES_BASE = "tagging-policies";
const TAGGING_POLICY_IDENTIFIER = ":taggingPolicyId";

export const TAGGING_POLICIES = concatenateUrl([TAGGING_POLICIES_BASE]);
export const TAGGING_POLICY = concatenateUrl([TAGGING_POLICIES_BASE, TAGGING_POLICY_IDENTIFIER]);
export const getTaggingPolicyUrl = (policyId) => TAGGING_POLICY.replace(TAGGING_POLICY_IDENTIFIER, policyId);

export const TAGGING_POLICY_CREATE = concatenateUrl([TAGGING_POLICIES_BASE, CREATE]);

// Organizations overview
const ORGANIZATIONS_OVERVIEW_BASE = "organizations";
export const ORGANIZATIONS_OVERVIEW = concatenateUrl([ORGANIZATIONS_OVERVIEW_BASE]);

// K8sRightsizing
const K8S_RIGHTSIZING_BASE = "k8s-rightsizing";
export const K8S_RIGHTSIZING = concatenateUrl([K8S_RIGHTSIZING_BASE]);

// Assignment rules
const ASSIGNMENT_RULE_IDENTIFIER = ":assignmentRuleId";
const ASSIGNMENT_RULES_BASE = "assignment-rules";
const ASSIGNMENT_RULE_BASE = "assignment-rule";

export const ASSIGNMENT_RULE = concatenateUrl([ASSIGNMENT_RULE_BASE]);

export const ASSIGNMENT_RULES = concatenateUrl([ASSIGNMENT_RULES_BASE]);

export const ASSIGNMENT_RULE_CREATE = concatenateUrl([ASSIGNMENT_RULE_BASE, CREATE]);
export const getCreateAssignmentRuleUrl = ({ conditions = [] } = {}) => {
  const parsedConditions = conditions.map(
    (condition) => `${ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER}[]=${JSON.stringify(condition)}`
  );
  return `${ASSIGNMENT_RULE_CREATE}${concatenateUrl([...parsedConditions], "?", "&")}`;
};

export const ASSIGNMENT_RULE_EDIT = concatenateUrl([ASSIGNMENT_RULE_BASE, ASSIGNMENT_RULE_IDENTIFIER, EDIT]);
export const getEditAssignmentRuleUrl = (ruleId) => ASSIGNMENT_RULE_EDIT.replace(ASSIGNMENT_RULE_IDENTIFIER, ruleId);

// User management
export const USER_MANAGEMENT = concatenateUrl([USER_MANAGEMENT_BASE_URL]);

export const EMPLOYEES_INVITE = concatenateUrl([USER_MANAGEMENT_BASE_URL, INVITE]);

// Cloud account
export const CLOUD_ACCOUNTS = concatenateUrl([CLOUD_ACCOUNTS_BASE_URL]);
export const CLOUD_ACCOUNT = concatenateUrl([CLOUD_ACCOUNTS_BASE_URL, CLOUD_ACCOUNT_IDENTIFIER]);

export const getCloudAccountUrl = (cloudAccountId) => CLOUD_ACCOUNT.replace(CLOUD_ACCOUNT_IDENTIFIER, cloudAccountId);

export const CLOUD_ACCOUNT_CONNECT = concatenateUrl([CLOUD_ACCOUNT_BASE_URL, CONNECT]);
export const CLOUD_ACCOUNT_CONNECT_K8S = concatenateUrl([CLOUD_ACCOUNT_CONNECT, `${DATASOURCE_TYPE}=${KUBERNETES}`], "", "?");

// Resources
const RESOURCES_BASE = "resources";
export const RESOURCES = concatenateUrl([RESOURCES_BASE]);
export const INSTANCES = concatenateUrl([RESOURCES, `${RESOURCE_TYPE_FILTER}=Instance`], "", "?");
export const VOLUMES = concatenateUrl([RESOURCES, `${RESOURCE_TYPE_FILTER}=Volume`], "", "?");

export const RESOURCE = concatenateUrl([RESOURCES_BASE, RESOURCE_IDENTIFIER]);
export const getResourceUrl = (resourceId) => RESOURCE.replace(RESOURCE_IDENTIFIER, resourceId);

export const getThisMonthResourcesUrl = () => {
  const { today, startOfMonth } = getCurrentMonthRange(true);
  return `${RESOURCES}?startDate=${startOfMonth}&endDate=${today}`;
};

export const getLast30DaysResourcesUrl = () => {
  const { endDate: today, startDate: startOfMonth } = getLast30DaysRange();
  return `${RESOURCES}?startDate=${startOfMonth}&endDate=${today}`;
};

export const getThisMonthResourcesByPoolUrl = (poolId) => {
  const thisMonthResourcesUrl = getThisMonthResourcesUrl();
  return `${thisMonthResourcesUrl}&${POOL_ID_FILTER}=${getPoolIdWithSubPoolsEncoded(poolId)}`;
};

export const getThisMonthResourcesByPoolWithoutSubpoolsUrl = (poolId) => {
  const thisMonthResourcesUrl = getThisMonthResourcesUrl();
  return `${thisMonthResourcesUrl}&${POOL_ID_FILTER}=${poolId}`;
};

export const RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME = "breakdownBy";
export const GROUP_TYPE_PARAM_NAME = "groupType";
export const GROUP_BY_PARAM_NAME = "groupBy";
export const DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME = "categorizedBy";
export const DAILY_EXPENSES_SPLIT_PARAMETER_NAME = "expenses";
export const DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME = "resourceCountBreakdownBy";
export const SHOW_EXPENSES_DAILY_BREAKDOWN_PARAMETER_NAME = "showExpensesDailyBreakdown";
export const RESOURCES_PERSPECTIVE_PARAMETER_NAME = "perspective";
export const RESOURCES_SELECTED_PERSPECTIVE_PARAMETER_NAME = "selectedPerspective";

export const getResourcesExpensesUrl = ({
  sStartDate,
  sEndDate,
  computedParams,
  perspective,
  organizationId,
  ...restFilters
}) => {
  const query = formQueryString({
    [START_DATE_FILTER]: sStartDate,
    [END_DATE_FILTER]: sEndDate,
    [RESOURCES_PERSPECTIVE_PARAMETER_NAME]: perspective,
    organizationId,
    ...restFilters
  });

  const computedParameters = computedParams ? `${computedParams}` : "";

  return `${RESOURCES}${concatenateUrl(
    [query, computedParameters].filter((el) => el !== ""),
    "?",
    "&"
  )}`;
};

const PERSPECTIVES = "perspectives";
export const RESOURCE_PERSPECTIVES = concatenateUrl([RESOURCES_BASE, PERSPECTIVES]);

// Resource assignment rules
export const RESOURCE_ASSIGNMENT_RULE_CREATE = concatenateUrl([
  RESOURCES_BASE,
  RESOURCE_IDENTIFIER,
  ASSIGNMENT_RULE_BASE,
  CREATE
]);
export const getCreateResourceAssignmentRuleUrl = (resourceId) =>
  RESOURCE_ASSIGNMENT_RULE_CREATE.replace(RESOURCE_IDENTIFIER, resourceId);

export const TTL_ANALYSIS_BASE = "ttl-analysis";
export const TTL_ANALYSIS = concatenateUrl([TTL_ANALYSIS_BASE]);
export const POOL_TTL_ANALYSIS = concatenateUrl([POOLS_BASE, POOL_IDENTIFIER, TTL_ANALYSIS_BASE]);
export const getPoolTtlAnalysis = (poolId) => POOL_TTL_ANALYSIS.replace(POOL_IDENTIFIER, poolId);

export const EVENTS = "/events";
export const INTEGRATIONS = "/integrations";
export const INTEGRATION_QUERY_PARAM = "id";

export const SETTINGS = "/settings";
export const getSettingsUrl = (tab) => (tab ? `${SETTINGS}?${TAB_QUERY_PARAM_NAME}=${tab}` : SETTINGS);

// Recommendation
const RECOMMENDATIONS_BASE = "recommendations";
export const RECOMMENDATIONS = concatenateUrl([RECOMMENDATIONS_BASE]);

export const getIntegrationsUrl = (sectionId) =>
  sectionId ? `${INTEGRATIONS}?${INTEGRATION_QUERY_PARAM}=${sectionId}` : INTEGRATIONS;

export const RECOMMENDATION_CATEGORY_QUERY_PARAMETER = "category";
export const RECOMMENDATION_SERVICE_QUERY_PARAMETER = "service";
export const RECOMMENDATION_VIEW_QUERY_PARAMETER = "view";

export const getRecommendationsUrl = ({ category, service } = {}) => {
  const categoryParameter = category ? `${RECOMMENDATION_CATEGORY_QUERY_PARAMETER}=${category}` : "";
  const serviceParameter = service ? `${RECOMMENDATION_SERVICE_QUERY_PARAMETER}=${service}` : "";

  return buildQueryParameters(RECOMMENDATIONS, [categoryParameter, serviceParameter]);
};

// Recommendation archive
const ARCHIVED_RECOMMENDATIONS_BASE = "archived-recommendations";
export const ARCHIVED_RECOMMENDATIONS = concatenateUrl([ARCHIVED_RECOMMENDATIONS_BASE]);

// Cloud Cost Comparison
const CLOUD_COST_COMPARISON_BASE = "cloud-cost-comparison";
export const CLOUD_COST_COMPARISON = concatenateUrl([CLOUD_COST_COMPARISON_BASE]);

// RI/SP coverage
const RI_SP_COVERAGE_BASE = "ri-sp-coverage";
export const RI_SP_COVERAGE = concatenateUrl([RECOMMENDATIONS_BASE, RI_SP_COVERAGE_BASE]);

export const RI_SP_QUERY_PARAMETERS = Object.freeze({
  START_DATE: START_DATE_FILTER,
  END_DATE: END_DATE_FILTER,
  DATA_SOURCE_ID: "dataSourceId"
});

export const getRiSpCoverageUrl = ({ secondsStartDate, secondsEndDate, dataSourceId } = {}) => {
  const query = formQueryString({
    [RI_SP_QUERY_PARAMETERS.START_DATE]: secondsStartDate,
    [RI_SP_QUERY_PARAMETERS.END_DATE]: secondsEndDate,
    [RI_SP_QUERY_PARAMETERS.DATA_SOURCE_ID]: dataSourceId
  });

  return `${RI_SP_COVERAGE}${query ? `?${query}` : ""}`;
};

// ML profiling
const ML_TASK_IDENTIFIER = ":taskId";
const ML_TASK_RUN_IDENTIFIER = ":runId";
const ML_TASK_METRIC_IDENTIFIER = ":metricId";
const ML_RUNSET_TEMPLATE_IDENTIFIER = ":templateId";
const ML_RUNSET_IDENTIFIER = ":runsetId";
const ML_EXECUTORS_BASE = "executors";
const ML_RUNSET_TEMPLATES_BASE = "runset-templates";
const ML_TASKS_BASE = "tasks";
const ML_TASK_METRICS_BASE = "metrics";
const ML_DATASETS_BASE = "datasets";
const ML_DATASET_IDENTIFIER = ":datasetId";
const ML_MODELS_BASE = "models";
const ML_MODEL_IDENTIFIER = ":modelId";

export const ML_RUNSETS_BASE = "runsets";
export const ML_RUN_BASE = "run";

export const ML_TASKS = concatenateUrl([ML_TASKS_BASE]);
export const ML_TASK_CREATE = concatenateUrl([ML_TASKS_BASE, CREATE]);

export const ML_SETUP_LEADERBOARDS = concatenateUrl([ML_TASKS_BASE, ML_TASK_IDENTIFIER, "setup-leaderboards"]);
export const getMlSetupLeaderboards = (taskId) => ML_SETUP_LEADERBOARDS.replace(ML_TASK_IDENTIFIER, taskId);

export const ML_DATASETS = concatenateUrl([ML_DATASETS_BASE]);
export const ML_DATASET_CREATE = concatenateUrl([ML_DATASETS_BASE, CREATE]);
export const ML_DATASET_EDIT = concatenateUrl([ML_DATASETS_BASE, ML_DATASET_IDENTIFIER, EDIT]);
export const getEditMlDatasetUrl = (id) => ML_DATASET_EDIT.replace(ML_DATASET_IDENTIFIER, id);

export const ML_MODELS = concatenateUrl([ML_MODELS_BASE]);
export const ML_MODEL_CREATE = concatenateUrl([ML_MODELS_BASE, CREATE]);

export const ML_MODEL_EDIT = concatenateUrl([ML_MODELS_BASE, ML_MODEL_IDENTIFIER, EDIT]);
export const getEditMlModelUrl = (modelId: string) => ML_MODEL_EDIT.replace(ML_MODEL_IDENTIFIER, modelId);

export const ML_MODEL = concatenateUrl([ML_MODELS_BASE, ML_MODEL_IDENTIFIER]);
export const getMlModelUrl = (modelId: string) => ML_MODEL.replace(ML_MODEL_IDENTIFIER, modelId);

const ML_LAUNCH_BASE = "launch";

export const ML_TASK_METRICS = concatenateUrl([ML_TASKS_BASE, ML_TASK_METRICS_BASE]);
export const ML_TASK_METRIC_CREATE = concatenateUrl([ML_TASKS_BASE, ML_TASK_METRICS_BASE, CREATE]);
export const ML_TASK_METRIC_EDIT = concatenateUrl([ML_TASKS_BASE, ML_TASK_METRICS_BASE, ML_TASK_METRIC_IDENTIFIER, EDIT]);

export const getEditTaskMetricUrl = (metricId) => ML_TASK_METRIC_EDIT.replace(ML_TASK_METRIC_IDENTIFIER, metricId);

export const ML_TASK_DETAILS = concatenateUrl([ML_TASKS_BASE, ML_TASK_IDENTIFIER]);
export const getMlTaskDetailsUrl = (taskId) => ML_TASK_DETAILS.replace(ML_TASK_IDENTIFIER, taskId);

export const ML_TASK_EDIT = concatenateUrl([ML_TASKS_BASE, ML_TASK_IDENTIFIER, EDIT]);
export const getEditMlTaskUrl = (taskId, params) => {
  const base = ML_TASK_EDIT.replace(ML_TASK_IDENTIFIER, taskId);

  if (params) {
    return concatenateUrl(
      [
        base,
        Object.entries(params)
          .map(([name, value]) => `${name}=${value}`)
          .join("&")
      ],
      "",
      "?"
    );
  }

  return base;
};

export const ML_EXECUTORS = concatenateUrl([ML_TASKS_BASE, ML_EXECUTORS_BASE]);

export const ML_RUNSET_TEMPLATES = concatenateUrl([ML_RUNSET_TEMPLATES_BASE]);
export const ML_RUNSET_TEMPLATE_CREATE = concatenateUrl([ML_RUNSET_TEMPLATES_BASE, CREATE]);

export const ML_RUNSET_TEMPLATE = concatenateUrl([ML_RUNSET_TEMPLATES_BASE, ML_RUNSET_TEMPLATE_IDENTIFIER]);
export const getMlRunsetTemplateUrl = (templateId) => ML_RUNSET_TEMPLATE.replace(ML_RUNSET_TEMPLATE_IDENTIFIER, templateId);

export const ML_EDIT_RUNSET_TEMPLATE = concatenateUrl([ML_RUNSET_TEMPLATES_BASE, ML_RUNSET_TEMPLATE_IDENTIFIER, EDIT]);
export const getMlEditRunsetTemplateUrl = (templateId) =>
  ML_EDIT_RUNSET_TEMPLATE.replace(ML_RUNSET_TEMPLATE_IDENTIFIER, templateId);

export const ML_RUNSET_TEMPLATE_CONFIGURATION = concatenateUrl([
  ML_RUNSET_TEMPLATES_BASE,
  ML_RUNSET_TEMPLATE_IDENTIFIER,
  ML_LAUNCH_BASE
]);
export const getMlRunsetConfigurationUrl = (templateId) =>
  ML_RUNSET_TEMPLATE_CONFIGURATION.replace(ML_RUNSET_TEMPLATE_IDENTIFIER, templateId);

export const ML_RUNSET_DETAILS = concatenateUrl([ML_RUNSETS_BASE, ML_RUNSET_IDENTIFIER]);

export const getMlRunsetDetailsUrl = (runsetId) => ML_RUNSET_DETAILS.replace(ML_RUNSET_IDENTIFIER, runsetId);

export const ML_TASK_RUN = concatenateUrl([ML_TASKS_BASE, ML_TASK_IDENTIFIER, ML_RUN_BASE, ML_TASK_RUN_IDENTIFIER]);

export const getMlTaskRunUrl = (taskId, runId) =>
  ML_TASK_RUN.replace(ML_TASK_IDENTIFIER, taskId).replace(ML_TASK_RUN_IDENTIFIER, runId);

// Live demo
export const LIVE_DEMO = "/live-demo";

// Slack
const SLACK_BASE = "slack";
const SLACK_SECRET_IDENTIFIER = ":secret";

// Clusters
const CLUSTER_TYPES_BASE = "cluster-types";
const CLUSTER_TYPE_BASE = "cluster-type";

export const CLUSTER_TYPES = concatenateUrl([CLUSTER_TYPES_BASE]);
export const CLUSTER_TYPE_CREATE = concatenateUrl([CLUSTER_TYPE_BASE, CREATE]);

// Environments
const ENVIRONMENTS_BASE = "environments";

export const ENVIRONMENTS = concatenateUrl([ENVIRONMENTS_BASE]);
export const ENVIRONMENT_CREATE = concatenateUrl([ENVIRONMENTS_BASE, CREATE]);

// Slack
export const SLACK_CONNECT = concatenateUrl([SLACK_BASE, "connect", SLACK_SECRET_IDENTIFIER]);
export const getSlackConnectUrl = (secret) => SLACK_CONNECT.replace(SLACK_SECRET_IDENTIFIER, secret);

// Organization options
const ORGANIZATION_OPTIONS_BASE = "org-options";

export const ORGANIZATION_OPTIONS = concatenateUrl([ORGANIZATION_OPTIONS_BASE]);
export const ORGANIZATION_OPTIONS_CREATE = concatenateUrl([ORGANIZATION_OPTIONS_BASE, CREATE]);

// Jira
const JIRA_BASE = "jira";
const JIRA_SECRET_IDENTIFIER = ":secret";

export const JIRA_CONNECT = concatenateUrl([JIRA_BASE, "connect", JIRA_SECRET_IDENTIFIER]);

// Resource lifecycle
const RESOURCE_LIFECYCLE_BASE = "resource-lifecycle";
const POOL_POLICY = "pool-policy";
export const RESOURCE_LIFECYCLE = concatenateUrl([RESOURCE_LIFECYCLE_BASE]);
export const getResourceLifecycleUrl = (tab) =>
  tab ? `${RESOURCE_LIFECYCLE}?${TAB_QUERY_PARAM_NAME}=${tab}` : RESOURCE_LIFECYCLE;
export const RESOURCE_LIFECYCLE_CREATE_POOL_POLICY = concatenateUrl([RESOURCE_LIFECYCLE_BASE, POOL_POLICY, CREATE]);

const THEME_SETTINGS_BASE = "theme-settings";
export const THEME_SETTINGS = concatenateUrl([THEME_SETTINGS_BASE]);

// S3 duplicates finder
const S3_DUPLICATE_FINDER_BASE = "s3-duplicate-finder";
const S3_DUPLICATE_FINDER_CHECK_IDENTIFIER = ":checkId";

export const S3_DUPLICATE_FINDER = concatenateUrl([RECOMMENDATIONS_BASE, S3_DUPLICATE_FINDER_BASE]);
export const S3_DUPLICATE_FINDER_CHECK = concatenateUrl([
  RECOMMENDATIONS_BASE,
  S3_DUPLICATE_FINDER_BASE,
  S3_DUPLICATE_FINDER_CHECK_IDENTIFIER
]);
export const getS3DuplicateFinderCheck = (id) => S3_DUPLICATE_FINDER_CHECK.replace(S3_DUPLICATE_FINDER_CHECK_IDENTIFIER, id);

// Instances Schedules
const POWER_SCHEDULES_BASE = "power-schedules";
const POWER_SCHEDULE_IDENTIFIER = ":powerScheduleId";

export const POWER_SCHEDULES = concatenateUrl([POWER_SCHEDULES_BASE]);
export const POWER_SCHEDULE_DETAILS = concatenateUrl([POWER_SCHEDULES_BASE, POWER_SCHEDULE_IDENTIFIER]);
export const CREATE_POWER_SCHEDULE = concatenateUrl([POWER_SCHEDULES_BASE, CREATE]);
export const EDIT_POWER_SCHEDULE = concatenateUrl([POWER_SCHEDULES_BASE, POWER_SCHEDULE_IDENTIFIER, EDIT]);

export const getPowerScheduleDetailsUrl = (id: string) => POWER_SCHEDULE_DETAILS.replace(POWER_SCHEDULE_IDENTIFIER, id);
export const getEditPowerScheduleUrl = (id: string) => EDIT_POWER_SCHEDULE.replace(POWER_SCHEDULE_IDENTIFIER, id);

// External urls
export const PRODUCTION = "https://my.optscale.com";
export const DEMO = "https://demo.optscale.com";
export const HYSTAX = "https://hystax.com";
export const HYSTAX_PRIVACY_POLICY = "https://hystax.com/privacy-policy/";

export const FINOPS = "https://finopsinpractice.org/";
export const FINOPS_FEATURES = "https://finopsinpractice.org/finops-in-practice-features-for-optscale/";
export const FINOPS_HOWTOS = "https://finopsinpractice.org/blog-posts-list-for-optscale/";

export const JIRA_MARKETPLACE = "https://marketplace.atlassian.com/apps/1227110/hystax-optscale-for-jira";

// Hystax documentation urls
export const DOCS_HYSTAX_OPTSCALE = "https://hystax.com/documentation/optscale/";
export const DOCS_HYSTAX_AUTO_BILLING_AWS = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_aws_root_cur.html#automatic-billing-data-import-in-aws`;
export const DOCS_HYSTAX_DISCOVER_RESOURCES = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_aws_linked.html#discover-resources`;
export const DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_alibaba.html`;
export const DOCS_HYSTAX_CONNECT_GCP_CLOUD = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_gcp.html`;
export const DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_azure.html`;
export const DOCS_HYSTAX_RESOURCE_CONSTRAINTS = `${DOCS_HYSTAX_OPTSCALE}resource_constraints.html`;
export const DOCS_HYSTAX_CLUSTERS = `${DOCS_HYSTAX_OPTSCALE}clusters.html`;
export const DOCS_HYSTAX_CLEANUP_SCRIPTS = `${DOCS_HYSTAX_OPTSCALE}optscales_recommendations.html#clean-up-scripts-based-on-optscale-s-recommendations`;
export const DOCS_HYSTAX_SLACK_INTEGRATION = `${DOCS_HYSTAX_OPTSCALE}integrations.html#slack-app`;

// Hystax open source links
export const GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR =
  "https://github.com/hystax/helm-charts/tree/main/charts/kube-cost-metrics-collector";
export const GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS = "https://github.com/hystax/optscale_tools/tree/main/extract_linked_reports";
export const GITHUB_HYSTAX_OPTSCALE_REPO = "https://github.com/hystax/optscale";
export const PYPI_OPTSCALE_ARCEE = "https://pypi.org/project/optscale-arcee";

// Nebius documentation
export const NEBIUS_CREATE_SERVICE_ACCOUNT = "https://nebius.com/il/docs/iam/quickstart-sa#create-sa";
export const NEBIUS_CREATING_AUTHORIZED_KEYS = "https://nebius.com/il/docs/iam/operations/authorized-key/create";
export const NEBIUS_CREATING_STATIC_ACCESS_KEYS = "https://nebius.com/il/docs/iam/operations/sa/create-access-key";
export const NEBIUS_GET_FOLDER_REPORT = "https://nebius.com/il/docs/billing/operations/get-folder-report";

// Databricks documentation
export const DATABRICKS_CREATE_SERVICE_PRINCIPAL = "https://docs.databricks.com/en/dev-tools/authentication-oauth.html";

// Emails
export const EMAIL_SUPPORT = "support@hystax.com";
export const EMAIL_SALES = "sales@hystax.com";
export const EMAIL_INFO = "info@hystax.com";

export const isProduction = () => window.location.origin === PRODUCTION;
export const isDemo = () => window.location.origin === DEMO;

export const USER_EMAIL_QUERY_PARAMETER_NAME = "userEmail";
