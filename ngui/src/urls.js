import {
  RECOMMENDATION_CATEGORY_QUERY_PARAMETER,
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

export const HOME = "/";
export const getHomeUrl = (organizationId) =>
  organizationId ? concatenateUrl([HOME, `?organizationId=${organizationId}`], "", "") : HOME;
export const SHOW_POLICY_QUERY_PARAM = "showPolicy";
export const HOME_FIRST_TIME = `/?${SHOW_POLICY_QUERY_PARAM}=true`;
export const LOGIN = "/login";
export const SIGNOUT = "/signout";
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

export const BUSINESS_INTELLIGENCE = "/business-intelligence";

// Technical audit
export const TECHNICAL_AUDIT = "/technical-audit";

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
export const POOL = concatenateUrl([POOLS_BASE, POOL_IDENTIFIER]);
export const POOLS = concatenateUrl([POOLS_BASE]);
export const getPoolUrl = (poolId) => POOL.replace(POOL_IDENTIFIER, poolId);

export const POOL_CREATE = concatenateUrl([POOLS_BASE, POOL_IDENTIFIER, CREATE]);
export const getCreatePoolUrl = (parentPoolId) => POOL_CREATE.replace(POOL_IDENTIFIER, parentPoolId);

export const POOL_EDIT_BASE = concatenateUrl([POOL_BASE]);
export const POOL_EDIT = concatenateUrl([POOL_BASE, POOL_IDENTIFIER, EDIT]);

export const getEditPoolUrl = (poolId) => POOL_EDIT.replace(POOL_IDENTIFIER, poolId);

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

export const TAGGING_POLICY = concatenateUrl([TAGGING_POLICIES_BASE, TAGGING_POLICY_IDENTIFIER]);
export const TAGGING_POLICIES = concatenateUrl([TAGGING_POLICIES_BASE]);
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

// Pool assignment rules
export const POOL_ASSIGNMENT_RULE_CREATE = concatenateUrl([POOLS_BASE, POOL_IDENTIFIER, ASSIGNMENT_RULE_BASE, CREATE]);
export const getCreatePoolAssignmentRuleUrl = (poolId) => POOL_ASSIGNMENT_RULE_CREATE.replace(POOL_IDENTIFIER, poolId);

export const POOL_ASSIGNMENT_RULE_EDIT = concatenateUrl([
  POOLS_BASE,
  POOL_IDENTIFIER,
  ASSIGNMENT_RULE_BASE,
  ASSIGNMENT_RULE_IDENTIFIER,
  EDIT
]);
export const getEditPoolAssignmentRuleUrl = (poolId, ruleId) =>
  POOL_ASSIGNMENT_RULE_EDIT.replace(POOL_IDENTIFIER, poolId).replace(ASSIGNMENT_RULE_IDENTIFIER, ruleId);

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

export const getResourcesExpensesUrl = ({ sStartDate, sEndDate, computedParams, ...restFilters }) => {
  const query = formQueryString({
    [START_DATE_FILTER]: sStartDate,
    [END_DATE_FILTER]: sEndDate,
    ...restFilters
  });

  const computedParameters = computedParams ? `${computedParams}` : "";

  return `${RESOURCES}${concatenateUrl(
    [query, computedParameters].filter((el) => el !== ""),
    "?",
    "&"
  )}`;
};

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
export const CLOUD_MIGRATION = "/cloud-migration";
export const DISASTER_RECOVERY = "/disaster-recovery";
export const SETTINGS = "/settings";
export const getSettingsUrl = (tab) => (tab ? `${SETTINGS}?${TAB_QUERY_PARAM_NAME}=${tab}` : SETTINGS);

// Recommendation
const RECOMMENDATIONS_BASE = "recommendations";
export const RECOMMENDATIONS = concatenateUrl([RECOMMENDATIONS_BASE]);

const RECOMMENDATION_IDENTIFIER = ":recommendationType";
export const RECOMMENDATION_SETTINGS = concatenateUrl([RECOMMENDATIONS_BASE, RECOMMENDATION_IDENTIFIER, "settings"]);
export const getRecommendationSettingsUrl = (recommendationType) =>
  RECOMMENDATION_SETTINGS.replace(RECOMMENDATION_IDENTIFIER, recommendationType);

export const getIntegrationsUrl = (sectionId) =>
  sectionId ? `${INTEGRATIONS}?${INTEGRATION_QUERY_PARAM}=${sectionId}` : INTEGRATIONS;

export const getRecommendationsUrl = ({ category } = {}) => {
  const categoryParameter = category ? `${RECOMMENDATION_CATEGORY_QUERY_PARAMETER}=${category}` : "";

  return buildQueryParameters(RECOMMENDATIONS, [categoryParameter]);
};

// Recommendation archive
const ARCHIVED_RECOMMENDATIONS_BASE = "archived-recommendations";
export const ARCHIVED_RECOMMENDATIONS = concatenateUrl([ARCHIVED_RECOMMENDATIONS_BASE]);

// Cloud health
export const CLOUD_HEALTH = "/cloud-health";

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
export const RESOURCE_LIFECYCLE_CREATE_POOL_POLICY = concatenateUrl([RESOURCE_LIFECYCLE_BASE, POOL_POLICY, CREATE]);

const THEME_SETTINGS_BASE = "theme-settings";
export const THEME_SETTINGS = concatenateUrl([THEME_SETTINGS_BASE]);

// External urls
export const PRODUCTION = "https://my.optscale.com";
export const DEMO = "https://demo.optscale.com";
export const HYSTAX = "https://hystax.com";
export const HYSTAX_CLOUD_MIGRATION = "https://hystax.com/cloud-migration/";
export const HYSTAX_DISASTER_RECOVERY = "https://hystax.com/disaster-recovery/";

export const HYSTAX_CLOUD_MIGRATION_AWS = "https://hystax.com/live-cloud-migration-to-aws/";
export const HYSTAX_CLOUD_MIGRATION_AZURE = "https://hystax.com/live-cloud-migration-to-azure/";
export const HYSTAX_CLOUD_MIGRATION_GCP = "https://hystax.com/live-cloud-migration-to-gcp/";
export const HYSTAX_CLOUD_MIGRATION_VMWARE = "https://hystax.com/live-cloud-migration-to-vmware/";
export const HYSTAX_CLOUD_MIGRATION_ALIBABA = "https://hystax.com/live-cloud-migration-to-alibaba/";
export const HYSTAX_CLOUD_MIGRATION_OPENSTACK = "https://hystax.com/live-cloud-migration-to-openstack/";

export const HYSTAX_DISASTER_RECOVERY_AWS = "https://hystax.com/disaster-recovery-to-aws/";
export const HYSTAX_DISASTER_RECOVERY_AZURE = "https://hystax.com/disaster-recovery-to-azure/";
export const HYSTAX_DISASTER_RECOVERY_GCP = "https://hystax.com/disaster-recovery-to-gcp/";
export const HYSTAX_DISASTER_RECOVERY_VMWARE = "https://hystax.com/disaster-recovery-to-vmware/";
export const HYSTAX_DISASTER_RECOVERY_ALIBABA = "https://hystax.com/disaster-recovery-to-alibaba/";
export const HYSTAX_DISASTER_RECOVERY_OPENSTACK = "https://hystax.com/disaster-recovery-to-openstack/";

export const FINOPS = "https://finopsinpractice.org/";
export const FINOPS_FEATURES = "https://finopsinpractice.org/finops-in-practice-features-for-optscale/";
export const FINOPS_HOWTOS = "https://finopsinpractice.org/blog-posts-list-for-optscale/";

export const AWS_MARKETPLACE = "https://aws.amazon.com/marketplace/pp/prodview-j2knb36hzq74o";
export const AZURE_MARKETPLACE =
  "https://azuremarketplace.microsoft.com/en-us/marketplace/apps/hystaxinc.hystax-optscale?tab=Overview";
export const ALIBABA_MARKETPLACE = "https://marketplace.alibabacloud.com/products/56718005/sgcmjj00025834.html";
export const DIGITAL_OCEAN_MARKETPLACE = "https://marketplace.digitalocean.com/apps/free-cost-management";
export const JIRA_MARKETPLACE = "https://marketplace.atlassian.com/apps/1227110/hystax-optscale-for-jira";

export const CODECLIMATE = "https://github.com/codeclimate/codeclimate";
export const CODECLIMATE_GITLAB_WRAPPER = "https://gitlab.com/gitlab-org/ci-cd/codequality";
export const SEMGREP = "https://github.com/returntocorp/semgrep";
export const SEMGREP_GUIDE = "https://semgrep.dev/docs/getting-started/";
export const SEMGREP_SETTING = "https://github.com/returntocorp/semgrep/issues/2387#issuecomment-759411656";
export const CLOC = "https://github.com/AlDanial/cloc";
export const FINOPS_ASSESSMENT_SURVEY = "https://survey.hystax.com/zs/wuB33j";
export const TECHNICAL_AUDIT_SURVEY = "https://survey.hystax.com/zs/jED7SK";

// Hystax documentation urls
export const DOCS_HYSTAX_OPTSCALE = "https://hystax.com/documentation/optscale/";
export const DOCS_HYSTAX_AUTO_BILLING_AWS = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_aws_root_cur.html#automatic-billing-data-import-in-aws`;
export const DOCS_HYSTAX_DISCOVER_RESOURCES = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_aws_linked.html#discover-resources`;
export const DOCS_HYSTAX_CONNECT_ALIBABA_CLOUD = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_alibaba.html`;
export const DOCS_HYSTAX_CONNECT_AZURE_ACCOUNT = `${DOCS_HYSTAX_OPTSCALE}e2e_guides/e2e_azure.html`;
export const DOCS_HYSTAX_RESOURCE_CONSTRAINTS = `${DOCS_HYSTAX_OPTSCALE}resource_constraints.html`;
export const DOCS_HYSTAX_CLUSTERS = `${DOCS_HYSTAX_OPTSCALE}clusters.html`;
export const DOCS_HYSTAX_CLEANUP_SCRIPTS = `${DOCS_HYSTAX_OPTSCALE}optscales_recommendations.html#clean-up-scripts-based-on-optscale-s-recommendations`;
export const DOCS_HYSTAX_SLACK_INTEGRATION = `${DOCS_HYSTAX_OPTSCALE}integrations.html#slack-app`;

// Hystax open source links
export const GITHUB_HYSTAX_K8S_COST_METRICS_COLLECTOR = "https://github.com/hystax/optscale-k8s-cost-metrics-collector";
export const GITHUB_HYSTAX_EXTRACT_LINKED_REPORTS = "https://github.com/hystax/optscale_tools/tree/main/extract_linked_reports";

// Emails
export const EMAIL_SUPPORT = "support@hystax.com";
export const EMAIL_INFO = "info@hystax.com";

export const HYSTAX_MARKETPLACES_ANCHOR = "https://hystax.com/optscale/#marketplaces";
export const HYSTAX_FORRESTER =
  "https://hystax.com/hystax-named-to-forresters-report-of-top-cloud-cost-management-and-optimization-providers/";

export const isProduction = () => window.location.origin === PRODUCTION;
export const isDemo = () => window.location.origin === DEMO;

export const getUrlWithNextQueryParam = (target, next, saveParameters = false) => {
  // TODO: Use query string to build returned url
  const savedParameters = saveParameters ? `&${window.location.search?.substr(1)}` : "";
  return next && next !== HOME ? `${target}?next=${next.replace(/&/g, "%26")}${savedParameters}` : target;
};
