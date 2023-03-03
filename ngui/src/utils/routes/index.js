import acceptInvitationRoute from "./acceptInvitationRoute";
import acceptInvitationsRoute from "./acceptInvitationsRoute";
import anomaliesRoute from "./anomaliesRoute";
import anomalyRoute from "./anomalyRoute";
import archivedRecommendationsRoute from "./archivedRecommendationsRoute";
import assignmentRulesRoute from "./assignmentRulesRoute";
import BaseRoute from "./baseRoute";
import cloudExpensesRoute from "./cloudExpensesRoute";
import cloudMigrationRoute from "./cloudMigrationRoute";
import clusterTypesRoute from "./clusterTypesRoute";
import connectJiraRoute from "./connectJiraRoute";
import connectSlackRoute from "./connectSlackRoute";
import createAnomalyRoute from "./createAnomalyRoute";
import createAssignmentRuleRoute from "./createAssignmentRuleRoute";
import createClusterTypeRoute from "./createClusterTypeRoute";
import createDataSourceRoute from "./createDataSourceRoute";
import createEnvironmentRoute from "./createEnvironmentRoute";
import createMlApplicationParameterRoute from "./createMlApplicationParameterRoute";
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
import editMlApplicationParameterRoute from "./editMlApplicationParameterRoute";
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
import mlApplicationsGlobalParametersRoute from "./mlApplicationsGlobalParametersRoute";
import mlApplicationsRoute from "./mlApplicationsRoute";
import mlEditApplicationRoute from "./mlEditApplicationRoute";
import mlExecutorsRoute from "./mlExecutorsRoute";
import mlModelCreateRoute from "./mlModelCreateRoute";
import mlModelDetailsRoute from "./mlModelDetailsRoute";
import mlModelRunRoute from "./mlModelRunRoute";
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
import recommendationSettingsRoute from "./recommendationSettingsRoute";
import recommendationsRoute from "./recommendationsRoute";
import registerRoute from "./registerRoute";
import resetPasswordRoute from "./resetPasswordRoute";
import resourceLifecycleRoute from "./resourceLifecycleRoute";
import resourceRoute from "./resourceRoute";
import resourcesPerspectives from "./resourcesPerspectives";
import resourcesRoute from "./resourcesRoute";
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
  recommendationSettingsRoute,
  connectSlackRoute,
  connectJiraRoute,
  clusterTypesRoute,
  environmentsRoute,
  createEnvironmentRoute,
  createClusterTypeRoute,
  integrationsRoute,
  organizationOptionsRoute,
  resourceLifecycleRoute,
  createPoolPolicyRoute,
  themeSettingsRoute,
  notFoundRoute,
  createMlApplicationParameterRoute,
  editMlApplicationParameterRoute,
  mlEditApplicationRoute,
  mlExecutorsRoute,
  mlModelCreateRoute,
  mlModelDetailsRoute,
  mlModelRunRoute,
  mlApplicationsGlobalParametersRoute,
  mlApplicationsRoute
];

export default BaseRoute;
