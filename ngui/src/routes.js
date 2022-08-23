import { lazy } from "react";
import MainLayout from "layouts/MainLayout";
import SecondaryLayout from "layouts/SecondaryLayout";
import {
  ASSIGNMENT_RULE_CREATE,
  POOL_ASSIGNMENT_RULE_CREATE,
  POOL_ASSIGNMENT_RULE_EDIT,
  ASSIGNMENT_RULES,
  ASSIGNMENT_RULE_EDIT,
  POOL,
  POOL_CREATE,
  POOL_EDIT,
  ANOMALIES,
  CLOUD_ACCOUNT,
  CLOUD_ACCOUNTS,
  CLOUD_ACCOUNT_CONNECT,
  CLOUD_EXPENSES,
  POOL_EXPENSES,
  OWNER_EXPENSES,
  USER_MANAGEMENT,
  EMPLOYEES_INVITE,
  EVENTS,
  HOME,
  LOGIN,
  SIGNOUT,
  EXPENSES,
  EXPENSES_MAP,
  LIVE_DEMO,
  REGISTER,
  RESET_PASSWORD,
  RESOURCES,
  RESOURCE,
  SETTINGS,
  CLOUD_MIGRATION,
  DISASTER_RECOVERY,
  ACCEPT_INVITATION,
  ACCEPT_INVITATIONS,
  RECOMMENDATIONS,
  CLOUD_HEALTH,
  TTL_ANALYSIS,
  POOL_TTL_ANALYSIS,
  RESOURCE_ASSIGNMENT_RULE_CREATE,
  SLACK_CONNECT,
  ORGANIZATIONS_OVERVIEW,
  CLUSTER_TYPES,
  CLUSTER_TYPE_CREATE,
  ENVIRONMENTS,
  ENVIRONMENT_CREATE,
  INTEGRATIONS,
  ORGANIZATION_OPTIONS,
  JIRA_CONNECT,
  INVITED,
  ANOMALY_CREATE,
  ANOMALY,
  POOLS,
  QUOTAS_AND_BUDGETS,
  QUOTA_AND_BUDGET,
  QUOTA_AND_BUDGET_CREATE,
  TAGGING_POLICIES,
  TAGGING_POLICY_CREATE,
  TAGGING_POLICY,
  RESOURCE_LIFECYCLE,
  RESOURCE_LIFECYCLE_CREATE_POOL_POLICY,
  FINOPS_PORTAL,
  RECOMMENDATION_SETTINGS,
  K8S_RIGHTSIZING,
  ARCHIVED_RECOMMENDATIONS,
  THEME_SETTINGS,
  BUSINESS_INTELLIGENCE
} from "urls";

const LazyAcceptInvitation = lazy(() => import("pages/AcceptInvitation"));
const LazyAcceptInvitations = lazy(() => import("pages/AcceptInvitations"));
const LazyAssignmentRules = lazy(() => import("pages/AssignmentRules"));
const LazyAuthorization = lazy(() => import("pages/Authorization"));
const LazyCloudAccountDetails = lazy(() => import("pages/CloudAccountDetails"));
const LazyCloudAccountsOverview = lazy(() => import("pages/CloudAccountsOverview"));
const LazyCloudHealth = lazy(() => import("pages/CloudHealth"));
const LazyCloudMigration = lazy(() => import("pages/CloudMigration"));
const LazyClusterTypes = lazy(() => import("pages/ClusterTypes"));
const LazyConnectCloudAccount = lazy(() => import("pages/ConnectCloudAccount"));
const LazyConnectJira = lazy(() => import("pages/ConnectJira"));
const LazyConnectSlack = lazy(() => import("pages/ConnectSlack"));
const LazyCreateAssignmentRule = lazy(() => import("pages/CreateAssignmentRule"));
const LazyCreateClusterType = lazy(() => import("pages/CreateClusterType"));
const LazyCreateEnvironment = lazy(() => import("pages/CreateEnvironment"));
const LazyCreatePool = lazy(() => import("pages/CreatePool"));
const LazyCreateResourceAssignmentRule = lazy(() => import("pages/CreateResourceAssignmentRule"));
const LazyDashboard = lazy(() => import("pages/Dashboard"));
const LazyDisasterRecovery = lazy(() => import("pages/DisasterRecovery"));
const LazyEditAssignmentRule = lazy(() => import("pages/EditAssignmentRule"));
const LazyEditPool = lazy(() => import("pages/EditPool"));
const LazyEmployees = lazy(() => import("pages/Employees"));
const LazyEnvironments = lazy(() => import("pages/Environments"));
const LazyError = lazy(() => import("pages/Error"));
const LazyEvents = lazy(() => import("pages/Events"));
const LazyExpenses = lazy(() => import("pages/Expenses"));
const LazyOwnerExpensesBreakdown = lazy(() => import("pages/OwnerExpensesBreakdown"));
const LazyPoolExpensesBreakdown = lazy(() => import("pages/PoolExpensesBreakdown"));
const LazyCloudExpensesBreakdown = lazy(() => import("pages/CloudExpensesBreakdown"));
const LazyExpensesMap = lazy(() => import("pages/ExpensesMap"));
const LazyFinOpsPortal = lazy(() => import("pages/FinOpsPortal"));
const LazyBusinessIntelligence = lazy(() => import("pages/BusinessIntelligence"));
const LazyIntegrations = lazy(() => import("pages/Integrations"));
const LazyInvited = lazy(() => import("pages/Invited"));
const LazyInviteEmployees = lazy(() => import("pages/InviteEmployees"));
const LazyLiveDemo = lazy(() => import("pages/LiveDemo"));
const LazyOrganizationOptions = lazy(() => import("pages/OrganizationOptions"));
const LazyOrganizationOverview = lazy(() => import("pages/OrganizationOverview"));
const LazyPoolsRedirect = lazy(() => import("pages/Pools"));
const LazyOrganizationsOverview = lazy(() => import("pages/OrganizationsOverview"));
const LazyRecommendations = lazy(() => import("pages/Recommendations"));
const LazyArchivedRecommendations = lazy(() => import("./pages/ArchivedRecommendations/ArchivedRecommendations"));
const LazyRecommendationSettings = lazy(() => import("pages/RecommendationSettings"));
const LazyResetPassword = lazy(() => import("pages/ResetPassword"));
const LazyResource = lazy(() => import("pages/Resource"));
const LazyResources = lazy(() => import("pages/Resources"));
const LazySettings = lazy(() => import("pages/Settings"));
const LazySignout = lazy(() => import("pages/Signout"));
const LazyTtlAnalysis = lazy(() => import("pages/TtlAnalysis"));
const LazyAnomalies = lazy(() => import("pages/Anomalies"));
const LazyK8sRightsizing = lazy(() => import("pages/K8sRightsizing"));
const LazyCreateOrganizationConstraint = lazy(() => import("pages/CreateOrganizationConstraint"));
const LazyOrganizationConstraint = lazy(() => import("pages/OrganizationConstraint"));
const LazyQuotasAndBudgets = lazy(() => import("pages/QuotasAndBudgets"));
const LazyTaggingPolicies = lazy(() => import("pages/TaggingPolicies"));
const LazyResourceLifecycle = lazy(() => import("pages/ResourceLifecycle"));
const LazyCreatePoolPolicy = lazy(() => import("pages/CreatePoolPolicy"));
const LazyThemeSettings = lazy(() => import("pages/ThemeSettings"));

const routes = [
  {
    key: "assignmentRuleCreate",
    link: ASSIGNMENT_RULE_CREATE,
    component: LazyCreateAssignmentRule,
    layout: MainLayout
  },
  {
    key: "assignmentRuleEdit",
    link: ASSIGNMENT_RULE_EDIT,
    component: LazyEditAssignmentRule,
    layout: MainLayout
  },
  {
    key: "pooleAssignmentRuleCreate",
    link: POOL_ASSIGNMENT_RULE_CREATE,
    component: LazyCreateAssignmentRule,
    layout: MainLayout
  },
  {
    key: "poolAssignmentRuleEdit",
    link: POOL_ASSIGNMENT_RULE_EDIT,
    component: LazyEditAssignmentRule,
    layout: MainLayout
  },
  {
    key: "poolOverview",
    link: POOL,
    component: LazyOrganizationOverview,
    layout: MainLayout
  },
  {
    key: "poolsRedirectToMain",
    link: POOLS,
    component: LazyPoolsRedirect,
    layout: MainLayout
  },
  {
    key: "taggingPolicies",
    link: TAGGING_POLICIES,
    component: LazyTaggingPolicies,
    layout: MainLayout
  },
  {
    key: "createTaggingPolicy",
    link: TAGGING_POLICY_CREATE,
    component: LazyCreateOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "anomalies",
    link: ANOMALIES,
    component: LazyAnomalies,
    layout: MainLayout
  },
  {
    key: "k8sRightsizing",
    link: K8S_RIGHTSIZING,
    component: LazyK8sRightsizing,
    layout: MainLayout
  },
  {
    key: "createOrganizationConstraint",
    link: ANOMALY_CREATE,
    component: LazyCreateOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "createQuotaAndBudgetPolicy",
    link: QUOTA_AND_BUDGET_CREATE,
    component: LazyCreateOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "anomaly",
    link: ANOMALY,
    component: LazyOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "quota",
    link: QUOTA_AND_BUDGET,
    component: LazyOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "quotasAndBudgets",
    link: QUOTAS_AND_BUDGETS,
    component: LazyQuotasAndBudgets,
    layout: MainLayout
  },
  {
    key: "quotasAndBudgets",
    link: QUOTAS_AND_BUDGETS,
    component: LazyQuotasAndBudgets,
    layout: MainLayout
  },
  {
    key: "taggingPolicy",
    link: TAGGING_POLICY,
    component: LazyOrganizationConstraint,
    layout: MainLayout
  },
  {
    key: "OrganizationsOverview",
    link: ORGANIZATIONS_OVERVIEW,
    component: LazyOrganizationsOverview,
    layout: SecondaryLayout
  },
  {
    key: "assignmentRules",
    link: ASSIGNMENT_RULES,
    component: LazyAssignmentRules,
    layout: MainLayout
  },
  {
    key: "poolCreate",
    link: POOL_CREATE,
    component: LazyCreatePool,
    layout: MainLayout
  },
  {
    key: "poolEdit",
    link: POOL_EDIT,
    component: LazyEditPool,
    layout: MainLayout
  },
  {
    key: "users",
    link: USER_MANAGEMENT,
    component: LazyEmployees,
    layout: MainLayout
  },
  {
    key: "employeeCreate",
    link: EMPLOYEES_INVITE,
    component: LazyInviteEmployees,
    layout: MainLayout
  },
  {
    key: "cloudAccountsOverview",
    link: CLOUD_ACCOUNTS,
    component: LazyCloudAccountsOverview,
    layout: MainLayout
  },
  {
    key: "cloudAccountOverviewDetails",
    link: CLOUD_ACCOUNT,
    component: LazyCloudAccountDetails,
    layout: MainLayout
  },
  {
    key: "cloudAccountCreate",
    link: CLOUD_ACCOUNT_CONNECT,
    component: LazyConnectCloudAccount,
    layout: MainLayout
  },
  {
    key: "resources",
    link: RESOURCES,
    component: LazyResources,
    layout: MainLayout
  },
  {
    key: "ttl-analysis",
    link: TTL_ANALYSIS,
    component: LazyTtlAnalysis,
    layout: MainLayout
  },
  {
    key: "pool-ttl-analysis",
    link: POOL_TTL_ANALYSIS,
    component: LazyTtlAnalysis,
    layout: MainLayout
  },
  {
    key: "resource",
    link: RESOURCE,
    component: LazyResource,
    layout: MainLayout
  },
  {
    key: "events",
    link: EVENTS,
    component: LazyEvents,
    layout: MainLayout
  },
  {
    key: "finOpsPortal",
    link: FINOPS_PORTAL,
    component: LazyFinOpsPortal,
    layout: MainLayout
  },
  {
    key: "businessIntelligence",
    link: BUSINESS_INTELLIGENCE,
    component: LazyBusinessIntelligence,
    layout: MainLayout
  },
  {
    key: "settings",
    link: SETTINGS,
    component: LazySettings,
    layout: MainLayout
  },
  {
    key: "cloudMigration",
    link: CLOUD_MIGRATION,
    component: LazyCloudMigration,
    layout: MainLayout
  },
  {
    key: "disasterRecovery",
    link: DISASTER_RECOVERY,
    component: LazyDisasterRecovery,
    layout: MainLayout
  },
  {
    key: "home",
    link: HOME,
    component: LazyDashboard,
    layout: MainLayout
  },
  {
    key: "login",
    link: LOGIN,
    component: LazyAuthorization,
    isTokenRequired: false
  },
  {
    key: "signout",
    link: SIGNOUT,
    component: LazySignout,
    isTokenRequired: false
  },
  {
    key: "register",
    link: REGISTER,
    component: LazyAuthorization,
    isTokenRequired: false
  },
  {
    key: "invited",
    link: INVITED,
    component: LazyInvited,
    isTokenRequired: false
  },
  {
    key: "liveDemo",
    link: LIVE_DEMO,
    component: LazyLiveDemo,
    isTokenRequired: false
  },
  {
    key: "resetPassword",
    link: RESET_PASSWORD,
    component: LazyResetPassword,
    isTokenRequired: false
  },
  {
    key: "expenses",
    link: EXPENSES,
    component: LazyExpenses,
    layout: MainLayout
  },
  {
    key: "expensesMap",
    link: EXPENSES_MAP,
    component: LazyExpensesMap,
    layout: MainLayout
  },
  {
    key: "cloudExpenses",
    link: CLOUD_EXPENSES,
    component: LazyCloudExpensesBreakdown,
    layout: MainLayout
  },
  {
    key: "ownerExpenses",
    link: OWNER_EXPENSES,
    component: LazyOwnerExpensesBreakdown,
    layout: MainLayout
  },
  {
    key: "poolExpenses",
    link: POOL_EXPENSES,
    component: LazyPoolExpensesBreakdown,
    layout: MainLayout
  },
  {
    key: "acceptInvitation",
    link: ACCEPT_INVITATION,
    component: LazyAcceptInvitation
  },
  {
    key: "acceptInvitations",
    link: ACCEPT_INVITATIONS,
    component: LazyAcceptInvitations
  },
  {
    key: "recommendations",
    link: RECOMMENDATIONS,
    component: LazyRecommendations,
    layout: MainLayout
  },
  {
    key: "archive",
    link: ARCHIVED_RECOMMENDATIONS,
    component: LazyArchivedRecommendations,
    layout: MainLayout
  },
  {
    key: "recommendationSettings",
    link: RECOMMENDATION_SETTINGS,
    component: LazyRecommendationSettings,
    layout: MainLayout
  },
  {
    key: "cloudHealth",
    link: CLOUD_HEALTH,
    component: LazyCloudHealth,
    layout: MainLayout
  },
  {
    key: "resourceAssignmentRuleCreate",
    link: RESOURCE_ASSIGNMENT_RULE_CREATE,
    component: LazyCreateResourceAssignmentRule,
    layout: MainLayout
  },
  {
    key: "slackConnect",
    link: SLACK_CONNECT,
    component: LazyConnectSlack
  },
  {
    key: "jiraConnect",
    link: JIRA_CONNECT,
    component: LazyConnectJira
  },
  {
    key: "clusterTypes",
    link: CLUSTER_TYPES,
    component: LazyClusterTypes,
    layout: MainLayout
  },
  {
    key: "environments",
    link: ENVIRONMENTS,
    component: LazyEnvironments,
    layout: MainLayout
  },
  {
    key: "environmentsCreate",
    link: ENVIRONMENT_CREATE,
    component: LazyCreateEnvironment,
    layout: MainLayout
  },
  {
    key: "clusterTypesCreate",
    link: CLUSTER_TYPE_CREATE,
    component: LazyCreateClusterType,
    layout: MainLayout
  },
  {
    key: "integrations",
    link: INTEGRATIONS,
    component: LazyIntegrations,
    layout: MainLayout
  },
  {
    key: "organizationOptions",
    link: ORGANIZATION_OPTIONS,
    component: LazyOrganizationOptions,
    layout: MainLayout
  },
  {
    key: "resourceLifecycle",
    link: RESOURCE_LIFECYCLE,
    component: LazyResourceLifecycle,
    layout: MainLayout
  },
  {
    key: "createPoolPolicy",
    link: RESOURCE_LIFECYCLE_CREATE_POOL_POLICY,
    component: LazyCreatePoolPolicy,
    layout: MainLayout
  },
  {
    key: "themeSettings",
    link: THEME_SETTINGS,
    component: LazyThemeSettings,
    layout: MainLayout
  },
  {
    key: "notFound",
    component: LazyError,
    layout: MainLayout,
    context: { messageId: "notFound" },
    link: "*"
  }
];

export default routes;
