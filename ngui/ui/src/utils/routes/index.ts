import acceptInvitationRoute from "./acceptInvitationRoute";
import acceptInvitationsRoute from "./acceptInvitationsRoute";
import anomaliesRoute from "./anomaliesRoute";
import anomalyRoute from "./anomalyRoute";
import archivedRecommendationsRoute from "./archivedRecommendationsRoute";
import assignmentRulesRoute from "./assignmentRulesRoute";
import BaseRoute from "./baseRoute";
import biExportRoute from "./biExportRoute";
import biExportsRoute from "./biExportsRoute";
import cloudCostComparisonRoute from "./cloudCostComparisonRoute";
import cloudExpensesRoute from "./cloudExpensesRoute";
import clusterTypesRoute from "./clusterTypesRoute";
import connectJiraRoute from "./connectJiraRoute";
import connectSlackRoute from "./connectSlackRoute";
import createAnomalyRoute from "./createAnomalyRoute";
import createAssignmentRuleRoute from "./createAssignmentRuleRoute";
import createBIExportRoute from "./createBIExportRoute";
import createClusterTypeRoute from "./createClusterTypeRoute";
import createDataSourceRoute from "./createDataSourceRoute";
import createEnvironmentRoute from "./createEnvironmentRoute";
import createMlModelParameterRoute from "./createMlModelParameterRoute";
import createPoolPolicyRoute from "./createPoolPolicyRoute";
import createPowerScheduleRoute from "./createPowerScheduleRoute";
import createQuotaAndBudgetPolicyRoute from "./createQuotaAndBudgetPolicyRoute";
import createResourceAssignmentRuleRoute from "./createResourceAssignmentRuleRoute";
import createTaggingPolicyRoute from "./createTaggingPolicyRoute";
import dataSourceOverviewRoute from "./dataSourceOverviewRoute";
import dataSourcesRoute from "./dataSourcesRoute";
import editAssignmentRuleRoute from "./editAssignmentRuleRoute";
import editBIExportRoute from "./editBIExportRoute";
import editMlModelParameterRoute from "./editMlModelParameterRoute";
import editPowerScheduleRoute from "./editPowerScheduleRoute";
import environmentsRoute from "./environmentsRoute";
import eventsRoute from "./eventsRoute";
import expensesMapRoute from "./expensesMapRoute";
import expensesRoute from "./expensesRoute";
import finOpsPortalRoute from "./finOpsPortalRoute";
import homeRoute from "./homeRoute";
import integrationsRoute from "./integrationsRoute";
import invitedRoute from "./invitedRoute";
import inviteEmployeesRoute from "./inviteEmployeesRoute";
import k8sRightsizingRoute from "./k8sRightsizingRoute";
import liveDemoRoute from "./liveDemoRoute";
import loginRoute from "./loginRoute";
import mlDatasetCreateRoute from "./mlDatasetCreateRoute";
import mlDatasetEditRoute from "./mlDatasetEditRoute";
import mlDatasetsRoute from "./mlDatasetsRoute";
import mlEditModelRoute from "./mlEditModelRoute";
import mlExecutorsRoute from "./mlExecutorsRoute";
import mlModelCreateRoute from "./mlModelCreateRoute";
import mlModelDetailsRoute from "./mlModelDetailsRoute";
import mlModelGlobalParametersRoute from "./mlModelGlobalParametersRoute";
import mlModelsRoute from "./mlModelsRoute";
import mlModuleRunRoute from "./mlModuleRunRoute";
import mlRunsetConfiguration from "./mlRunsetConfiguration";
import mlRunsetOverview from "./mlRunsetOverview";
import mlRunsetsRoute from "./mlRunsetsRoute";
import mlRunsetTemplateCreateRoute from "./mlRunsetTemplateCreateRoute";
import mlRunsetTemplateEditRoute from "./mlRunsetTemplateEditRoute";
import mlRunsetTemplateRoute from "./mlRunsetTemplateRoute";
import notFoundRoute from "./notFoundRoute";
import organizationOptionsRoute from "./organizationOptionsRoute";
import organizationsOverviewRoute from "./organizationsOverviewRoute";
import ownerExpensesRoute from "./ownerExpensesRoute";
import poolExpensesRoute from "./poolExpensesRoute";
import poolsRoute from "./poolsRoute";
import poolTtlAnalysisRoute from "./poolTtlAnalysisRoute";
import powerScheduleDetailsRoute from "./powerScheduleDetailsRoute";
import powerSchedulesRoute from "./powerSchedulesRoute";
import quotaRoute from "./quotaRoute";
import quotasRoute from "./quotasRoute";
import recommendationsRoute from "./recommendationsRoute";
import registerRoute from "./registerRoute";
import resetPasswordRoute from "./resetPasswordRoute";
import resourceLifecycleRoute from "./resourceLifecycleRoute";
import resourceRoute from "./resourceRoute";
import resourcesPerspectives from "./resourcesPerspectives";
import resourcesRoute from "./resourcesRoute";
import riSpRoute from "./riSpRoute";
import s3DuplicateFinderRoute from "./s3DuplicateFinderRoute";
import s3DuplicatesCheckRoute from "./s3DuplicatesCheckRoute";
import settingsRoute from "./settingsRoute";
import setupLeaderboardRoute from "./setupLeaderboardRoute";
import taggingPoliciesRoute from "./taggingPoliciesRoute";
import taggingPolicyRoute from "./taggingPolicyRoute";
import themeSettingsRoute from "./themeSettingsRoute";
import ttlAnalysisRoute from "./ttlAnalysisRoute";
import usersRoute from "./usersRoute";

export const routes = [
  acceptInvitationRoute,
  acceptInvitationsRoute,
  anomaliesRoute,
  anomalyRoute,
  assignmentRulesRoute,
  createAssignmentRuleRoute,
  editAssignmentRuleRoute,
  createResourceAssignmentRuleRoute,
  organizationsOverviewRoute,
  poolsRoute,
  taggingPoliciesRoute,
  taggingPolicyRoute,
  createTaggingPolicyRoute,
  k8sRightsizingRoute,
  createAnomalyRoute,
  createQuotaAndBudgetPolicyRoute,
  quotaRoute,
  quotasRoute,
  usersRoute,
  inviteEmployeesRoute,
  dataSourcesRoute,
  dataSourceOverviewRoute,
  createDataSourceRoute,
  resourcesRoute,
  resourceRoute,
  ttlAnalysisRoute,
  poolTtlAnalysisRoute,
  eventsRoute,
  finOpsPortalRoute,
  settingsRoute,
  homeRoute,
  loginRoute,
  registerRoute,
  invitedRoute,
  liveDemoRoute,
  resetPasswordRoute,
  resourcesPerspectives,
  expensesRoute,
  expensesMapRoute,
  cloudExpensesRoute,
  ownerExpensesRoute,
  poolExpensesRoute,
  recommendationsRoute,
  archivedRecommendationsRoute,
  connectSlackRoute,
  connectJiraRoute,
  clusterTypesRoute,
  environmentsRoute,
  createEnvironmentRoute,
  createClusterTypeRoute,
  riSpRoute,
  integrationsRoute,
  organizationOptionsRoute,
  resourceLifecycleRoute,
  createPoolPolicyRoute,
  themeSettingsRoute,
  createMlModelParameterRoute,
  editMlModelParameterRoute,
  mlEditModelRoute,
  mlExecutorsRoute,
  mlRunsetsRoute,
  mlModelCreateRoute,
  mlDatasetsRoute,
  mlDatasetCreateRoute,
  mlDatasetEditRoute,
  mlModelDetailsRoute,
  mlModuleRunRoute,
  mlModelGlobalParametersRoute,
  mlModelsRoute,
  mlRunsetTemplateCreateRoute,
  mlRunsetConfiguration,
  mlRunsetOverview,
  mlRunsetTemplateRoute,
  mlRunsetTemplateEditRoute,
  biExportsRoute,
  biExportRoute,
  createBIExportRoute,
  editBIExportRoute,
  cloudCostComparisonRoute,
  s3DuplicateFinderRoute,
  s3DuplicatesCheckRoute,
  powerSchedulesRoute,
  createPowerScheduleRoute,
  powerScheduleDetailsRoute,
  setupLeaderboardRoute,
  editPowerScheduleRoute,
  // React router 6.x does not require the not found route (*) to be at the end,
  // but the matchPath hook that is used in the DocsPanel component seems to honor the order.
  // Moving it to the bottom for "safety" reasons.
  // TODO: investigate https://reactrouter.com/en/main/hooks/use-route-error and switching to data routers https://reactrouter.com/en/main/routers/picking-a-router
  notFoundRoute
];

export const ALL_ROUTES_PATTERNS = Object.freeze(routes.map(({ link }) => link));

export default BaseRoute;
