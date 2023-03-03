import { MAP_RECOMMENDATION_TYPES, BE_TO_FE_MAP_RECOMMENDATION_TYPES } from "utils/constants";
import { categorizeRecommendations } from "utils/recommendationCategories";
import {
  GET_ORGANIZATION_OPTION,
  SET_ORGANIZATION_OPTION,
  GET_CLOUD_ACCOUNTS,
  SET_CLOUD_ACCOUNTS,
  DELETE_CLOUD_ACCOUNT,
  SET_CLOUD_ACCOUNT,
  GET_INVITATION,
  SET_INVITATION,
  SET_POOL,
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
  GET_TECHNICAL_AUDIT,
  SET_TECHNICAL_AUDIT,
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
  GET_ML_APPLICATION,
  SET_ML_APPLICATION
} from "./actionTypes";

export const onUpdateOrganizationOption = (data) => ({
  type: SET_ORGANIZATION_OPTION,
  payload: data,
  label: GET_ORGANIZATION_OPTION
});

export const onSuccessCreateCloudAccount = (data) => ({
  type: SET_CLOUD_ACCOUNT,
  payload: data,
  label: GET_CLOUD_ACCOUNTS
});

export const onSuccessDisconnectCloudAccount = (id) => () => ({
  type: DELETE_CLOUD_ACCOUNT,
  payload: { id },
  label: GET_CLOUD_ACCOUNTS
});

export const onSuccessUpdateInvitation = () => ({
  type: SET_INVITATION,
  payload: {},
  label: GET_INVITATION
});

export const onSuccessCreatePool = (data) => ({
  type: SET_POOL,
  payload: data,
  label: GET_POOL
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

export const onSuccessGetOptimizations = (data) => {
  const supportedOptimizationTypes = Object.keys(BE_TO_FE_MAP_RECOMMENDATION_TYPES);

  const getOptimizations = (optimizationName) =>
    data[optimizationName]
      ? Object.keys(data[optimizationName]).reduce((resultObject, optimizationKey) => {
          if (supportedOptimizationTypes.includes(optimizationKey)) {
            return {
              ...resultObject,
              [MAP_RECOMMENDATION_TYPES[optimizationKey]]: data[optimizationName][optimizationKey]
            };
          }
          return resultObject;
        }, {})
      : {};

  const optimizations = getOptimizations("optimizations");
  const dismissedOptimizations = getOptimizations("dismissed_optimizations");
  const excludedOptimizations = getOptimizations("excluded_optimizations");

  const { categorizedRecommendations, categoriesSizes } = categorizeRecommendations(
    optimizations,
    dismissedOptimizations,
    excludedOptimizations
  );

  return {
    type: SET_OPTIMIZATIONS,
    payload: {
      ...data,
      optimizations,
      dismissed_optimizations: dismissedOptimizations,
      excluded_optimizations: excludedOptimizations,
      categorizedRecommendations,
      categoriesSizes
    },
    label: GET_OPTIMIZATIONS
  };
};

export const onSuccessUpdateOptimizations = (data) => ({
  type: SET_OPTIMIZATIONS,
  payload: {
    last_completed: data.last_completed,
    next_run: data.next_run
  },
  label: GET_OPTIMIZATIONS
});

export const onSuccessGetCloudAccounts = (data) => ({
  type: SET_CLOUD_ACCOUNTS,
  payload: data,
  label: GET_CLOUD_ACCOUNTS
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

export const onUpdateTechnicalAudit = (data) => ({
  type: SET_TECHNICAL_AUDIT,
  payload: data,
  label: GET_TECHNICAL_AUDIT
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

export const onUpdateMlApplication = (data) => ({
  type: SET_ML_APPLICATION,
  payload: data,
  label: GET_ML_APPLICATION
});
