import {
  GET_ORGANIZATION_OPTION,
  SET_ORGANIZATION_OPTION,
  GET_INVITATION,
  SET_INVITATION,
  GET_POOL,
  DELETE_POOL,
  GET_CURRENT_EMPLOYEE,
  SET_CURRENT_EMPLOYEE,
  GET_ASSIGNMENT_RULES,
  SET_POOL_POLICY,
  GET_POOL_POLICIES,
  GET_RESOURCE,
  SET_RESOURCE_CONSTRAINT,
  DELETE_RESOURCE_CONSTRAINT,
  SET_OPTIMIZATIONS,
  GET_OPTIMIZATIONS,
  GET_LIVE_DEMO,
  SET_LIVE_DEMO,
  SET_ASSIGNMENT_RULES,
  SET_FINOPS_CHECKLIST,
  GET_FINOPS_CHECKLIST,
  UPDATE_POOL_EXPENSES_EXPORT,
  UPDATE_ENVIRONMENT_PROPERTY,
  CREATE_WEBHOOK,
  UPDATE_WEBHOOK,
  DELETE_WEBHOOK,
  GET_WEBHOOKS,
  CREATE_SSH_KEY,
  GET_SSH_KEYS,
  UPDATE_SSH_KEY,
  GET_ORGANIZATION_CONSTRAINT,
  UPDATE_ORGANIZATION_CONSTRAINT,
  GET_GLOBAL_POOL_POLICIES,
  UPDATE_GLOBAL_POOL_POLICY,
  GET_GLOBAL_RESOURCE_CONSTRAINTS,
  UPDATE_GLOBAL_RESOURCE_CONSTRAINT,
  UPDATE_ORGANIZATION_THEME_SETTINGS,
  GET_ORGANIZATION_THEME_SETTINGS,
  UPDATE_ORGANIZATION_PERSPECTIVES,
  GET_ORGANIZATION_PERSPECTIVES,
  CREATE_ORGANIZATION,
  UPDATE_ENVIRONMENT_SSH_REQUIREMENT,
  GET_ML_TASK,
  SET_ML_TASK,
  SET_OPTIMIZATIONS_OVERVIEW,
  GET_OPTIMIZATIONS_OVERVIEW,
  SET_OPTIMIZATION_DETAILS,
  GET_OPTIMIZATION_DETAILS,
  SET_ML_OPTIMIZATION_DETAILS,
  GET_ML_OPTIMIZATION_DETAILS,
  GET_ML_RUNSET_TEMPLATE,
  SET_ML_RUNSET_TEMPLATE,
  SET_BI_EXPORT,
  GET_BI_EXPORT,
  UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  GET_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  UPDATE_ML_LEADERBOARD_DATASET,
  GET_ML_LEADERBOARD_DATASET,
  SET_POWER_SCHEDULE,
  GET_POWER_SCHEDULE,
  SET_ML_MODEL,
  GET_ML_MODEL
} from "./actionTypes";

export const onUpdateOrganizationOption = (data) => ({
  type: SET_ORGANIZATION_OPTION,
  payload: data,
  label: GET_ORGANIZATION_OPTION
});

export const onSuccessUpdateInvitation = () => ({
  type: SET_INVITATION,
  payload: {},
  label: GET_INVITATION
});

export const onSuccessCreateOrganization = (data) => ({
  type: CREATE_ORGANIZATION,
  payload: data,
  label: CREATE_ORGANIZATION
});

export const onSuccessDeletePool = (id) => () => ({
  type: DELETE_POOL,
  payload: { id },
  label: GET_POOL
});

export const onSuccessGetCurrentEmployee = ({ employees = [] }) => ({
  type: SET_CURRENT_EMPLOYEE,
  payload: employees[0],
  label: GET_CURRENT_EMPLOYEE
});

export const onSuccessCreatePoolPolicy = (data) => ({
  type: SET_POOL_POLICY,
  payload: data,
  label: GET_POOL_POLICIES
});

export const onSuccessCreateResourceConstraint = (data) => ({
  type: SET_RESOURCE_CONSTRAINT,
  payload: data,
  label: GET_RESOURCE
});

export const onSuccessUpdateGlobalPoolPolicyLimit = (data) => ({
  type: UPDATE_GLOBAL_POOL_POLICY,
  payload: data,
  label: GET_GLOBAL_POOL_POLICIES
});

export const onSuccessUpdateGlobalResourceConstraintLimit = (data) => ({
  type: UPDATE_GLOBAL_RESOURCE_CONSTRAINT,
  payload: data,
  label: GET_GLOBAL_RESOURCE_CONSTRAINTS
});

export const onSuccessUpdateGlobalPoolPolicyActivity = (data) => ({
  type: UPDATE_GLOBAL_POOL_POLICY,
  payload: data,
  label: GET_GLOBAL_POOL_POLICIES
});

export const onSuccessDeleteResourceConstraint = (id) => ({
  type: DELETE_RESOURCE_CONSTRAINT,
  payload: id,
  label: GET_RESOURCE
});

export const onSuccessGetOptimizationsOverview = (data) => ({
  type: SET_OPTIMIZATIONS_OVERVIEW,
  payload: data,
  label: GET_OPTIMIZATIONS_OVERVIEW
});

export const onSuccessGetOptimizationDetails = (data) => ({
  type: SET_OPTIMIZATION_DETAILS,
  payload: data,
  label: GET_OPTIMIZATION_DETAILS
});

export const onSuccessGetMLOptimizationDetails = (data) => ({
  type: SET_ML_OPTIMIZATION_DETAILS,
  payload: data,
  label: GET_ML_OPTIMIZATION_DETAILS
});

export const onSuccessUpdateOptimizations = (data) => ({
  type: SET_OPTIMIZATIONS,
  payload: {
    last_completed: data.last_completed,
    next_run: data.next_run
  },
  label: GET_OPTIMIZATIONS
});

export const onSuccessCreateSshKey = (data) => ({
  type: CREATE_SSH_KEY,
  payload: data,
  label: GET_SSH_KEYS
});

export const onSuccessUpdateSshKey = (data) => ({
  type: UPDATE_SSH_KEY,
  payload: data,
  label: GET_SSH_KEYS
});

export const onSuccessCreateLiveDemo = (data) => ({
  type: SET_LIVE_DEMO,
  payload: data,
  label: GET_LIVE_DEMO
});

export const onSuccessUpdateAssignmentRulePriority = (data) => ({
  type: SET_ASSIGNMENT_RULES,
  payload: data,
  label: GET_ASSIGNMENT_RULES
});

export const onFinOpsChecklist = (data) => ({
  type: SET_FINOPS_CHECKLIST,
  payload: data,
  label: GET_FINOPS_CHECKLIST
});

export const onSuccessExportLinkChange = (data) => ({
  type: UPDATE_POOL_EXPENSES_EXPORT,
  payload: data,
  label: UPDATE_POOL_EXPENSES_EXPORT
});

export const onSuccessUpdateEnvironmentProperty = (data) => ({
  type: UPDATE_ENVIRONMENT_PROPERTY,
  payload: data,
  label: GET_RESOURCE
});

export const onSuccessUpdateEnvironmentSshRequirement = (data) => ({
  type: UPDATE_ENVIRONMENT_SSH_REQUIREMENT,
  payload: data,
  label: GET_RESOURCE
});

export const onSuccessCreateWebhook = (data) => ({
  type: CREATE_WEBHOOK,
  payload: data,
  label: GET_WEBHOOKS
});

export const onSuccessUpdateWebhook = (data) => ({
  type: UPDATE_WEBHOOK,
  payload: data,
  label: GET_WEBHOOKS
});

export const onSuccessDeleteWebhook = (id) => () => ({
  type: DELETE_WEBHOOK,
  payload: id,
  label: GET_WEBHOOKS
});

export const onSuccessUpdateAnomaly = (data) => ({
  type: UPDATE_ORGANIZATION_CONSTRAINT,
  payload: data,
  label: GET_ORGANIZATION_CONSTRAINT
});

export const onUpdateOrganizationThemeSettings = (data) => ({
  type: UPDATE_ORGANIZATION_THEME_SETTINGS,
  payload: data,
  label: GET_ORGANIZATION_THEME_SETTINGS
});

export const onUpdateOrganizationPerspectives = (data) => ({
  type: UPDATE_ORGANIZATION_PERSPECTIVES,
  payload: data,
  label: GET_ORGANIZATION_PERSPECTIVES
});

export const onUpdateMlTask = (data) => ({
  type: SET_ML_TASK,
  payload: data,
  label: GET_ML_TASK
});

export const onUpdateMlModel = (data) => ({
  type: SET_ML_MODEL,
  payload: data,
  label: GET_ML_MODEL
});

export const onUpdateMlRunsetTemplate = (data) => ({
  type: SET_ML_RUNSET_TEMPLATE,
  payload: data,
  label: GET_ML_RUNSET_TEMPLATE
});

export const onUpdateBIExport = (data) => ({
  type: SET_BI_EXPORT,
  payload: data,
  label: GET_BI_EXPORT
});

export const onUpdateS3DuplicatesOrganizationSettings = (data) => ({
  type: UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  payload: data,
  label: GET_S3_DUPLICATES_ORGANIZATION_SETTINGS
});

export const onUpdateMlLeaderboardDataset = (data) => ({
  type: UPDATE_ML_LEADERBOARD_DATASET,
  payload: data,
  label: GET_ML_LEADERBOARD_DATASET
});

export const onUpdatePowerSchedule = (data) => ({
  type: SET_POWER_SCHEDULE,
  payload: data,
  label: GET_POWER_SCHEDULE
});
