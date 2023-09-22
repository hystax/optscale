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
import cloudMigrationRoute from "./cloudMigrationRoute";
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
import createPoolAssignmentRuleRoute from "./createPoolAssignmentRuleRoute";
import createPoolPolicyRoute from "./createPoolPolicyRoute";
import createPoolRoute from "./createPoolRoute";
import createQuotaAndBudgetPolicyRoute from "./createQuotaAndBudgetPolicyRoute";
import createResourceAssignmentRuleRoute from "./createResourceAssignmentRuleRoute";
import createTaggingPolicyRoute from "./createTaggingPolicyRoute";
import dataSourceOverviewRoute from "./dataSourceOverviewRoute";
import dataSourcesRoute from "./dataSourcesRoute";
import disasterRecoveryRoute from "./disasterRecoveryRoute";
import editAssignmentRuleRoute from "./editAssignmentRuleRoute";
import editBIExportRoute from "./editBIExportRoute";
import editMlModelParameterRoute from "./editMlModelParameterRoute";
import editPoolAssignmentRuleRoute from "./editPoolAssignmentRuleRoute";
import editPoolRoute from "./editPoolRoute";
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
import organizationOverviewRoute from "./organizationOverviewRoute";
import organizationsOverviewRoute from "./organizationsOverviewRoute";
import ownerExpensesRoute from "./ownerExpensesRoute";
import poolExpensesRoute from "./poolExpensesRoute";
import poolsRoute from "./poolsRoute";
import poolTtlAnalysisRoute from "./poolTtlAnalysisRoute";
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
  createPoolRoute,
  editPoolRoute,
  editAssignmentRuleRoute,
  createPoolAssignmentRuleRoute,
  createResourceAssignmentRuleRoute,
  editPoolAssignmentRuleRoute,
  organizationOverviewRoute,
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
  cloudMigrationRoute,
  disasterRecoveryRoute,
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
  notFoundRoute,
  createMlModelParameterRoute,
  editMlModelParameterRoute,
  mlEditModelRoute,
  mlExecutorsRoute,
  mlRunsetsRoute,
  mlModelCreateRoute,
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
  s3DuplicatesCheckRoute
];

export default BaseRoute;
