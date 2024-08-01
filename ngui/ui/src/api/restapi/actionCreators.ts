import { handleSuccess } from "api/actionCreators";
import { MINUTE, HALF_HOUR, HOUR, ERROR_HANDLER_TYPE_LOCAL, SUCCESS_HANDLER_TYPE_ALERT } from "api/constants";
import { apiAction, getApiUrl, hashParams } from "api/utils";
import { DAILY_EXPENSE_LIMIT, TOTAL_EXPENSE_LIMIT, TTL } from "utils/constraints";
import {
  GET_ORGANIZATION_FEATURES,
  SET_ORGANIZATION_FEATURES,
  GET_ORGANIZATION_OPTIONS,
  SET_ORGANIZATION_OPTIONS,
  GET_ORGANIZATION_OPTION,
  GET_ORGANIZATION_CONSTRAINTS,
  SET_ORGANIZATION_CONSTRAINTS,
  DELETE_ORGANIZATION_OPTION,
  UPDATE_ORGANIZATION_OPTION,
  CREATE_ORGANIZATION_OPTION,
  SET_ORGANIZATION_OPTION,
  CREATE_DATA_SOURCE,
  GET_POOL,
  DELETE_DATA_SOURCE,
  UPDATE_DATA_SOURCE,
  SET_POOL,
  UPDATE_POOL,
  DELETE_POOL,
  GET_ORGANIZATIONS,
  SET_ORGANIZATIONS,
  GET_ORGANIZATIONS_OVERVIEW,
  SET_ORGANIZATIONS_OVERVIEW,
  CREATE_POOL,
  CREATE_ASSIGNMENT_RULE,
  GET_POOLS_EXPENSES,
  GET_CLOUDS_EXPENSES,
  GET_EMPLOYEES_EXPENSES,
  SET_POOL_EXPENSES_BREAKDOWN,
  SET_CLOUDS_EXPENSES,
  SET_EMPLOYEES_EXPENSES,
  UPLOAD_CLOUD_REPORT,
  UPLOAD_CODE_REPORT,
  SUBMIT_FOR_AUDIT,
  GET_INVITATION,
  SET_INVITATION,
  UPDATE_INVITATION,
  CREATE_INVITATIONS,
  GET_SPLIT_RESOURCES,
  SET_SPLIT_RESOURCES,
  GET_AVAILABLE_POOLS,
  SET_AVAILABLE_POOLS,
  GET_POOL_OWNERS,
  SET_POOL_OWNERS,
  GET_AUTHORIZED_EMPLOYEES,
  GET_EMPLOYEES,
  DELETE_EMPLOYEE,
  SET_AUTHORIZED_EMPLOYEES,
  SET_EMPLOYEES,
  GET_CURRENT_EMPLOYEE,
  CREATE_ORGANIZATION,
  GET_ORGANIZATION_EXPENSES,
  SET_ORGANIZATION_EXPENSES,
  GET_RAW_EXPENSES,
  SET_RAW_EXPENSES,
  GET_CLEAN_EXPENSES,
  GET_EXPENSES_SUMMARY,
  SET_CLEAN_EXPENSES,
  SET_EXPENSES_SUMMARY,
  GET_AVAILABLE_FILTERS,
  SET_AVAILABLE_FILTERS,
  GET_REGION_EXPENSES,
  SET_REGION_EXPENSES,
  GET_ASSIGNMENT_RULES,
  SET_ASSIGNMENT_RULES,
  DELETE_ASSIGNMENT_RULE,
  GET_ASSIGNMENT_RULE,
  SET_ASSIGNMENT_RULE,
  UPDATE_ASSIGNMENT_RULE,
  UPDATE_ASSIGNMENT_RULE_PRIORITY,
  GET_RESOURCE,
  SET_RESOURCE,
  CREATE_POOL_POLICY,
  SET_POOL_POLICIES,
  GET_POOL_POLICIES,
  UPDATE_POOL_POLICY_LIMIT,
  UPDATE_POOL_POLICY_ACTIVITY,
  CREATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  CREATE_TTL_RESOURCE_CONSTRAINT,
  UPDATE_TTL_RESOURCE_CONSTRAINT,
  UPDATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  DELETE_RESOURCE_CONSTRAINT,
  SET_RESOURCE_LIMIT_HITS,
  GET_RESOURCE_LIMIT_HITS,
  GET_OPTIMIZATIONS,
  UPDATE_OPTIMIZATIONS,
  GET_LIVE_DEMO,
  SET_LIVE_DEMO,
  CREATE_LIVE_DEMO,
  GET_TTL_ANALYSIS,
  SET_TTL_ANALYSIS,
  APPLY_ASSIGNMENT_RULES,
  UPDATE_RESOURCE_VISIBILITY,
  GET_FINOPS_CHECKLIST,
  SET_FINOPS_CHECKLIST,
  UPDATE_FINOPS_CHECKLIST,
  GET_CLUSTER_TYPES,
  SET_CLUSTER_TYPES,
  CREATE_CLUSTER_TYPE,
  DELETE_CLUSTER_TYPE,
  UPDATE_CLUSTER_TYPE_PRIORITY,
  APPLY_CLUSTER_TYPES,
  GET_ENVIRONMENTS,
  SET_ENVIRONMENTS,
  CREATE_ENVIRONMENT,
  DELETE_ENVIRONMENT,
  UPDATE_ENVIRONMENT_ACTIVITY,
  GET_ENVIRONMENT_BOOKINGS,
  SET_ENVIRONMENT_BOOKINGS,
  GET_WEBHOOKS,
  SET_WEBHOOKS,
  CREATE_WEBHOOK,
  UPDATE_WEBHOOK,
  DELETE_WEBHOOK,
  GET_SSH_KEYS,
  SET_SSH_KEYS,
  CREATE_SSH_KEY,
  UPDATE_SSH_KEY,
  DELETE_SSH_KEY,
  CREATE_POOL_EXPENSES_EXPORT,
  DELETE_POOL_EXPENSES_EXPORT,
  SET_COST_EXPLORER_POOL_EXPENSES,
  GET_DATA_SOURCE_NODES,
  SET_DATA_SOURCE_NODES,
  GET_RESOURCE_METRICS,
  SET_RESOURCE_METRICS,
  GET_RESOURCE_COST_MODEL,
  SET_RESOURCE_COST_MODEL,
  GET_DATASOURCE_SKUS,
  SET_DATASOURCE_SKUS,
  UPDATE_DATASOURCE_SKU,
  UPDATE_RESOURCE_COST_MODEL,
  MARK_RESOURCES_AS_ENVIRONMENTS,
  UPDATE_BOOKING,
  DELETE_BOOKING,
  UPDATE_RESOURCE,
  BOOK_ENVIRONMENT,
  SET_OPTIMIZATION_OPTIONS,
  GET_OPTIMIZATION_OPTIONS,
  UPDATE_OPTIMIZATION_OPTIONS,
  GET_ORGANIZATION_CALENDAR,
  SET_ORGANIZATION_CALENDAR,
  CALENDAR_SYNCHRONIZATION,
  DELETE_CALENDAR_SYNCHRONIZATION,
  UPDATE_ENVIRONMENT_PROPERTY,
  UPDATE_ORGANIZATION,
  DELETE_ORGANIZATION,
  SET_INVITATIONS,
  GET_INVITATIONS,
  CREATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  UPDATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
  SET_RESOURCE_COUNT_BREAKDOWN,
  GET_RESOURCE_COUNT_BREAKDOWN,
  SET_TAGS_BREAKDOWN,
  GET_TAGS_BREAKDOWN,
  SET_EXPENSES_DAILY_BREAKDOWN,
  GET_EXPENSES_DAILY_BREAKDOWN,
  CREATE_ORGANIZATION_CONSTRAINT,
  GET_ORGANIZATION_CONSTRAINT,
  SET_ORGANIZATION_CONSTRAINT,
  DELETE_ORGANIZATION_CONSTRAINT,
  UPDATE_ORGANIZATION_CONSTRAINT,
  GET_ORGANIZATION_LIMIT_HITS,
  SET_ORGANIZATION_LIMIT_HITS,
  GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS,
  SET_RECOMMENDATIONS_DOWNLOAD_OPTIONS,
  GET_GLOBAL_POOL_POLICIES,
  SET_GLOBAL_POOL_POLICIES,
  GET_GLOBAL_RESOURCE_CONSTRAINTS,
  SET_GLOBAL_RESOURCE_CONSTRAINTS,
  CREATE_GLOBAL_POOL_POLICY,
  UPDATE_GLOBAL_POOL_POLICY_LIMIT,
  UPDATE_GLOBAL_POOL_POLICY_ACTIVITY,
  UPDATE_GLOBAL_RESOURCE_CONSTRAINT_LIMIT,
  DELETE_GLOBAL_RESOURCE_CONSTRAINT,
  SET_TRAFFIC_EXPENSES,
  GET_TRAFFIC_EXPENSES,
  GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN,
  SET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN,
  GET_ARCHIVED_OPTIMIZATIONS_COUNT,
  SET_ARCHIVED_OPTIMIZATIONS_COUNT,
  GET_ARCHIVED_OPTIMIZATION_DETAILS,
  SET_ARCHIVED_OPTIMIZATION_DETAILS,
  SET_K8S_RIGHTSIZING,
  GET_K8S_RIGHTSIZING,
  UPDATE_ORGANIZATION_THEME_SETTINGS,
  SET_ORGANIZATION_THEME_SETTINGS,
  GET_ORGANIZATION_THEME_SETTINGS,
  SET_ORGANIZATION_PERSPECTIVES,
  GET_ORGANIZATION_PERSPECTIVES,
  UPDATE_ORGANIZATION_PERSPECTIVES,
  UPDATE_ENVIRONMENT_SSH_REQUIREMENT,
  GET_ML_TASKS,
  SET_ML_TASKS,
  GET_ML_LEADERBOARD,
  SET_ML_LEADERBOARD,
  CREATE_ML_LEADERBOARD,
  GET_ML_LEADERBOARD_DATASET_DETAILS,
  SET_ML_LEADERBOARD_DATASET_DETAILS,
  UPDATE_ML_LEADERBOARD,
  GET_ML_DATASETS,
  SET_ML_DATASETS,
  CREATE_ML_DATASET,
  GET_ML_DATASET,
  SET_ML_DATASET,
  UPDATE_ML_DATASET,
  DELETE_ML_DATASET,
  GET_ML_GLOBAL_METRICS,
  SET_ML_GLOBAL_METRICS,
  GET_ML_GLOBAL_METRIC,
  SET_ML_GLOBAL_METRIC,
  CREATE_GLOBAL_METRIC,
  UPDATE_GLOBAL_METRIC,
  DELETE_GLOBAL_METRIC,
  CREATE_ML_TASK,
  GET_PROFILING_TOKEN,
  SET_PROFILING_TOKEN,
  GET_ML_EXECUTORS,
  SET_ML_EXECUTORS,
  GET_ML_EXECUTORS_BREAKDOWN,
  SET_ML_EXECUTORS_BREAKDOWN,
  SET_ML_TASK,
  GET_ML_TASK,
  UPDATE_ML_TASK,
  DELETE_ML_TASK,
  SET_ML_TASK_RUNS,
  GET_ML_TASK_RUNS,
  SET_ML_RUN_DETAILS,
  GET_ML_RUN_DETAILS,
  SET_ML_RUN_DETAILS_BREAKDOWN,
  GET_ML_RUN_DETAILS_BREAKDOWN,
  SET_ML_TASK_RECOMMENDATIONS,
  GET_ML_TASK_RECOMMENDATIONS,
  GET_OPTIMIZATIONS_OVERVIEW,
  GET_OPTIMIZATION_DETAILS,
  GET_ML_OPTIMIZATION_DETAILS,
  SET_ML_RUNSET_TEMPLATES,
  GET_ML_RUNSET_TEMPLATES,
  SET_ML_RUNSET_TEMPLATE,
  GET_ML_RUNSET_TEMPLATE,
  CREATE_ML_RUNSET_TEMPLATE,
  DELETE_ML_RUNSET_TEMPLATE,
  UPDATE_ML_RUNSET_TEMPLATE,
  SET_ML_RUNSETS,
  GET_ML_RUNSETS,
  SET_ML_RUNSET,
  GET_ML_RUNSET,
  CREATE_ML_RUNSET,
  SET_ML_RUNSETS_RUNS,
  GET_ML_RUNSETS_RUNS,
  SET_ML_RUNSET_EXECUTORS,
  GET_ML_RUNSET_EXECUTORS,
  SET_DATA_SOURCES,
  GET_DATA_SOURCES,
  STOP_ML_RUNSET,
  SET_ORGANIZATION_BI_EXPORTS,
  GET_ORGANIZATION_BI_EXPORT,
  CREATE_ORGANIZATION_BI_EXPORT,
  GET_BI_EXPORT,
  SET_BI_EXPORT,
  DELETE_BI_EXPORT,
  UPDATE_BI_EXPORT,
  GET_RELEVANT_FLAVORS,
  SET_RELEVANT_FLAVORS,
  SET_ORGANIZATION_CLOUD_RESOURCES,
  SET_ORGANIZATION_GEMINIS,
  CREATE_ORGANIZATION_GEMINI,
  GET_GEMINI,
  SET_GEMINI,
  SET_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  GET_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS,
  GET_ORGANIZATION_GEMINIS,
  GET_ORGANIZATION_CLOUD_RESOURCES,
  CREATE_SURVEY,
  SET_POWER_SCHEDULES,
  GET_POWER_SCHEDULES,
  CREATE_POWER_SCHEDULES,
  GET_POWER_SCHEDULE,
  SET_POWER_SCHEDULE,
  DELETE_POWER_SCHEDULE,
  UPDATE_POWER_SCHEDULE,
  ATTACH_INSTANCES_TO_SCHEDULE,
  REMOVE_INSTANCES_FROM_SCHEDULE,
  SET_ML_TASK_RUNS_BULK,
  GET_ML_TASK_RUNS_BULK,
  GET_ML_LEADERBOARD_DATASETS,
  SET_ML_LEADERBOARD_DATASETS,
  CREATE_ML_LEADERBOARD_DATASET,
  UPDATE_ML_LEADERBOARD_DATASET,
  DELETE_ML_LEADERBOARD_DATASET,
  SET_ML_LEADERBOARD_DATASET,
  GET_ML_LEADERBOARD_DATASET,
  SET_LAYOUTS,
  GET_LAYOUTS,
  SET_LAYOUT,
  GET_LAYOUT,
  CREATE_LAYOUT,
  UPDATE_LAYOUT,
  DELETE_LAYOUT,
  SET_RESERVED_INSTANCES_BREAKDOWN,
  GET_RESERVED_INSTANCES_BREAKDOWN,
  SET_SAVING_PLANS_BREAKDOWN,
  GET_SAVING_PLANS_BREAKDOWN,
  SET_ML_MODELS,
  GET_ML_MODELS,
  CREATE_ML_MODEL,
  GET_ML_MODEL,
  SET_ML_MODEL,
  UPDATE_ML_MODEL,
  DELETE_ML_MODEL,
  GET_ML_TASK_MODEL_VERSIONS,
  UPDATE_ML_MODEL_VERSION,
  SET_ML_TASK_MODEL_VERSIONS,
  GET_ML_ARTIFACTS,
  SET_ML_ARTIFACTS,
  SET_ML_ARTIFACT,
  GET_ML_ARTIFACT,
  UPDATE_ML_ARTIFACT,
  CREATE_ML_ARTIFACT,
  DELETE_ML_ARTIFACT,
  SET_ML_DATASET_LABELS,
  GET_ML_DATASET_LABELS
} from "./actionTypes";
import {
  onUpdateOrganizationOption,
  onSuccessUpdateInvitation,
  onSuccessDeletePool,
  onSuccessGetCurrentEmployee,
  onSuccessCreatePoolPolicy,
  onSuccessCreateResourceConstraint,
  onSuccessDeleteResourceConstraint,
  onSuccessUpdateOptimizations,
  onSuccessCreateLiveDemo,
  onSuccessUpdateAssignmentRulePriority,
  onFinOpsChecklist,
  onSuccessExportLinkChange,
  onSuccessUpdateEnvironmentProperty,
  onSuccessCreateWebhook,
  onSuccessUpdateWebhook,
  onSuccessDeleteWebhook,
  onSuccessCreateSshKey,
  onSuccessUpdateSshKey,
  onSuccessUpdateAnomaly,
  onSuccessUpdateGlobalPoolPolicyLimit,
  onSuccessUpdateGlobalPoolPolicyActivity,
  onSuccessUpdateGlobalResourceConstraintLimit,
  onUpdateOrganizationThemeSettings,
  onUpdateOrganizationPerspectives,
  onSuccessCreateOrganization,
  onSuccessUpdateEnvironmentSshRequirement,
  onUpdateMlTask,
  onSuccessGetOptimizationsOverview,
  onSuccessGetOptimizationDetails,
  onSuccessGetMLOptimizationDetails,
  onUpdateMlRunsetTemplate,
  onUpdateBIExport,
  onUpdateS3DuplicatesOrganizationSettings,
  onUpdateMlLeaderboardDataset,
  onUpdatePowerSchedule,
  onUpdateMlModel,
  onUpdateMlArtifact
} from "./handlers";

export const API_URL = getApiUrl("restapi");

export const getOrganizationFeatures = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/features`,
    method: "GET",
    ttl: HOUR,
    onSuccess: handleSuccess(SET_ORGANIZATION_FEATURES),
    hash: hashParams(organizationId),
    label: GET_ORGANIZATION_FEATURES
  });

export const getOrganizationThemeSettings = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/theme_settings`,
    method: "GET",
    ttl: HOUR,
    onSuccess: handleSuccess(SET_ORGANIZATION_THEME_SETTINGS),
    hash: hashParams(organizationId),
    label: GET_ORGANIZATION_THEME_SETTINGS
  });

export const getOrganizationPerspectives = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/perspectives`,
    method: "GET",
    ttl: HOUR,
    onSuccess: handleSuccess(SET_ORGANIZATION_PERSPECTIVES),
    hash: hashParams(organizationId),
    label: GET_ORGANIZATION_PERSPECTIVES
  });

export const updateOrganizationPerspectives = (organizationId, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/perspectives`,
    method: "PATCH",
    onSuccess: onUpdateOrganizationPerspectives,
    label: UPDATE_ORGANIZATION_PERSPECTIVES,
    params: {
      value: JSON.stringify(value)
    }
  });

export const getOrganizationOptions = (organizationId, withValues = false) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ORGANIZATION_OPTIONS),
    hash: hashParams({ organizationId, withValues }),
    label: GET_ORGANIZATION_OPTIONS,
    params: {
      with_values: withValues
    }
  });

export const getOrganizationOption = (organizationId, name) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/${name}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ORGANIZATION_OPTION),
    hash: hashParams({ organizationId, name }),
    label: GET_ORGANIZATION_OPTION
  });

export const deleteOrganizationOption = (organizationId, name) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/${name}`,
    method: "DELETE",
    label: DELETE_ORGANIZATION_OPTION,
    affectedRequests: [GET_ORGANIZATION_OPTIONS]
  });

export const updateOrganizationOption = (organizationId, name, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/${name}`,
    method: "PATCH",
    onSuccess: onUpdateOrganizationOption,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    label: UPDATE_ORGANIZATION_OPTION,
    affectedRequests: [GET_ORGANIZATION_OPTIONS],
    params: {
      value: JSON.stringify(value)
    }
  });

export const updateOrganizationThemeSettings = (organizationId, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/theme_settings`,
    method: "PATCH",
    onSuccess: onUpdateOrganizationThemeSettings,
    label: UPDATE_ORGANIZATION_THEME_SETTINGS,
    params: {
      value: JSON.stringify(value)
    }
  });

// Creating an option via PATCH is correct
export const createOrganizationOption = (organizationId, name, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/${name}`,
    method: "PATCH",
    label: CREATE_ORGANIZATION_OPTION,
    affectedRequests: [GET_ORGANIZATION_OPTIONS],
    params: {
      value: JSON.stringify(value)
    }
  });

export const getOrganizationConstraints = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/organization_constraints`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ORGANIZATION_CONSTRAINTS),
    hash: hashParams({ ...params, organizationId }),
    label: GET_ORGANIZATION_CONSTRAINTS,
    params
  });

export const createOrganizationConstraint = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/organization_constraints`,
    method: "POST",
    label: CREATE_ORGANIZATION_CONSTRAINT,
    affectedRequests: [GET_ORGANIZATION_CONSTRAINTS],
    params
  });

export const getOrganizationConstraint = (id) =>
  apiAction({
    url: `${API_URL}/organization_constraints/${id}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ORGANIZATION_CONSTRAINT),
    hash: hashParams(id),
    label: GET_ORGANIZATION_CONSTRAINT
  });

export const deleteOrganizationConstraint = (id) =>
  apiAction({
    url: `${API_URL}/organization_constraints/${id}`,
    method: "DELETE",
    label: DELETE_ORGANIZATION_CONSTRAINT,
    affectedRequests: [GET_ORGANIZATION_CONSTRAINTS]
  });

export const updateOrganizationConstraint = (id, params) =>
  apiAction({
    url: `${API_URL}/organization_constraints/${id}`,
    method: "PATCH",
    label: UPDATE_ORGANIZATION_CONSTRAINT,
    affectedRequests: [GET_ORGANIZATION_CONSTRAINTS],
    onSuccess: onSuccessUpdateAnomaly,
    params
  });

export const getDataSources = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_accounts`,
    method: "GET",
    onSuccess: handleSuccess(SET_DATA_SOURCES),
    label: GET_DATA_SOURCES,
    hash: hashParams(organizationId),
    ttl: 2 * MINUTE,
    params: {
      details: true
    }
  });

export const createDataSource = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_accounts`,
    method: "POST",
    affectedRequests: [GET_DATA_SOURCES, GET_AVAILABLE_FILTERS],
    label: CREATE_DATA_SOURCE,
    params
  });

export const disconnectDataSource = (id) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${id}`,
    method: "DELETE",
    affectedRequests: [GET_DATA_SOURCES, GET_AVAILABLE_FILTERS],
    label: DELETE_DATA_SOURCE
  });

export const uploadCloudReport = (cloudAccountId, file) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${cloudAccountId}/report_upload`,
    method: "POST",
    headersOverride: {
      "Content-Type": "application/octet-stream"
    },
    label: UPLOAD_CLOUD_REPORT,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    params: file
  });

export const uploadCodeReport = (organizationId, file) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/code_report_upload`,
    method: "POST",
    headersOverride: {
      "Content-Type": "application/octet-stream"
    },
    label: UPLOAD_CODE_REPORT,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    params: file
  });

export const submitForAudit = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/submit_for_audit`,
    method: "POST",
    label: SUBMIT_FOR_AUDIT
  });

export const updateDataSource = (id, params) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${id}`,
    method: "PATCH",
    label: UPDATE_DATA_SOURCE,
    affectedRequests: [GET_DATA_SOURCE_NODES],
    params
  });

export const getPool = (poolId, children = false, details = false) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_POOL),
    label: GET_POOL,
    ttl: 30 * MINUTE,
    hash: hashParams({ poolId, children, details }),
    params: {
      children,
      details
    }
  });

export const createOrganization = (name) =>
  apiAction({
    url: `${API_URL}/organizations`,
    method: "POST",
    onSuccess: onSuccessCreateOrganization,
    label: CREATE_ORGANIZATION,
    params: { name }
  });

export const createPool = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/pools`,
    method: "POST",
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    affectedRequests: [GET_AVAILABLE_POOLS, GET_AVAILABLE_FILTERS, GET_POOL],
    label: CREATE_POOL,
    params: {
      name: params.name,
      parent_id: params.parentId,
      limit: params.limit,
      purpose: params.type,
      auto_extension: params.autoExtension
    }
  });

export const updatePool = ({ id, name, limit, defaultOwnerId, type, autoExtension }) =>
  apiAction({
    url: `${API_URL}/pools/${id}`,
    method: "PATCH",
    label: UPDATE_POOL,
    affectedRequests: [
      GET_ASSIGNMENT_RULES,
      GET_AVAILABLE_POOLS,
      GET_CLEAN_EXPENSES,
      GET_POOLS_EXPENSES,
      GET_ASSIGNMENT_RULES,
      GET_ORGANIZATION_EXPENSES,
      GET_ORGANIZATIONS_OVERVIEW,
      GET_RESOURCE,
      GET_POOL
    ],
    params: {
      name,
      limit,
      default_owner_id: defaultOwnerId,
      purpose: type,
      auto_extension: autoExtension
    }
  });

export const deletePool = (id) =>
  apiAction({
    url: `${API_URL}/pools/${id}`,
    method: "DELETE",
    onSuccess: onSuccessDeletePool(id),
    affectedRequests: [GET_AVAILABLE_FILTERS],
    label: DELETE_POOL
  });

export const getOrganizations = () =>
  apiAction({
    url: `${API_URL}/organizations`,
    method: "GET",
    onSuccess: handleSuccess(SET_ORGANIZATIONS),
    ttl: HALF_HOUR,
    label: GET_ORGANIZATIONS
  });

export const deleteOrganization = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}`,
    method: "DELETE",
    label: DELETE_ORGANIZATION,
    affectedRequests: [GET_ORGANIZATIONS]
  });

export const updateOrganization = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}`,
    method: "PATCH",
    label: UPDATE_ORGANIZATION,
    affectedRequests: [GET_ORGANIZATIONS],
    params
  });

export const getOrganizationsOverview = (details = true) =>
  apiAction({
    url: `${API_URL}/organizations_overview`,
    method: "GET",
    onSuccess: handleSuccess(SET_ORGANIZATIONS_OVERVIEW),
    ttl: 5 * MINUTE,
    label: GET_ORGANIZATIONS_OVERVIEW,
    hash: hashParams({ details }),
    params: {
      details
    }
  });

export const getPoolExpenses = (poolId, params) =>
  apiAction({
    url: `${API_URL}/pools_expenses/${poolId}`,
    method: "GET",
    // The purpose of a custom success handler is to unify the response with and without a "filter by" parameter
    onSuccess: params.filterBy ? handleSuccess(SET_POOL_EXPENSES_BREAKDOWN) : handleSuccess(SET_COST_EXPLORER_POOL_EXPENSES),
    label: GET_POOLS_EXPENSES,
    ttl: MINUTE,
    hash: hashParams({ ...params, poolId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      filter_by: params.filterBy
    }
  });

export const getCloudsExpenses = (cloudAccountId, params) =>
  apiAction({
    url: `${API_URL}/clouds_expenses/${cloudAccountId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_CLOUDS_EXPENSES),
    label: GET_CLOUDS_EXPENSES,
    ttl: MINUTE,
    hash: hashParams({ ...params, cloudAccountId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      filter_by: params.filterBy
    }
  });

export const getEmployeesExpenses = (employeeId, params) =>
  apiAction({
    url: `${API_URL}/employees_expenses/${employeeId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_EMPLOYEES_EXPENSES),
    label: GET_EMPLOYEES_EXPENSES,
    ttl: MINUTE,
    hash: hashParams({ ...params, employeeId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      filter_by: params.filterBy
    }
  });

export const createInvitations = (invitations) =>
  apiAction({
    url: `${API_URL}/invites`,
    method: "POST",
    label: CREATE_INVITATIONS,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    params: { invites: invitations }
  });

export const getInvitation = (inviteId) =>
  apiAction({
    url: `${API_URL}/invites/${inviteId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_INVITATION),
    label: GET_INVITATION
  });

export const getInvitations = () =>
  apiAction({
    url: `${API_URL}/invites`,
    method: "GET",
    onSuccess: handleSuccess(SET_INVITATIONS),
    label: GET_INVITATIONS,
    ttl: HALF_HOUR
  });

export const updateInvitation = (inviteId, action) =>
  apiAction({
    url: `${API_URL}/invites/${inviteId}`,
    method: "PATCH",
    onSuccess: onSuccessUpdateInvitation,
    entityId: inviteId,
    label: UPDATE_INVITATION,
    affectedRequests: [GET_ORGANIZATIONS, GET_INVITATIONS],
    params: { action }
  });

export const splitResources = (organizationId, ids) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/split_resources/assign`,
    method: "POST",
    onSuccess: handleSuccess(SET_SPLIT_RESOURCES),
    label: GET_SPLIT_RESOURCES,
    params: ids
  });

export const getAvailablePools = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/pools`,
    method: "GET",
    onSuccess: handleSuccess(SET_AVAILABLE_POOLS),
    label: GET_AVAILABLE_POOLS,
    ttl: 30 * MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      permission: params.permission || ["INFO_ORGANIZATION"],
      condition: params.condition
    }
  });

export const getPoolOwners = (poolId: string, excludeMyself = false) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/employees`,
    method: "GET",
    onSuccess: handleSuccess(SET_POOL_OWNERS),
    label: GET_POOL_OWNERS,
    ttl: MINUTE,
    hash: hashParams({ poolId, excludeMyself }),
    params: {
      exclude_myself: excludeMyself
    }
  });

export const getAuthorizedEmployees = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/authorized_employees`,
    method: "GET",
    onSuccess: handleSuccess(SET_AUTHORIZED_EMPLOYEES),
    label: GET_AUTHORIZED_EMPLOYEES,
    ttl: 5 * MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      object_type: params.objectType,
      object_id: params.objectId,
      permission: params.permission || ["INFO_ORGANIZATION"]
    }
  });

export const getEmployees = (organizationId, roles = false, excludeMyself = false) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/employees`,
    method: "GET",
    onSuccess: handleSuccess(SET_EMPLOYEES),
    label: GET_EMPLOYEES,
    ttl: MINUTE,
    hash: hashParams({ organizationId, roles }),
    params: {
      roles,
      exclude_myself: excludeMyself
    }
  });

export const deleteEmployee = (employeeId, { newOwnerId }) =>
  apiAction({
    url: `${API_URL}/employees/${employeeId}`,
    method: "DELETE",
    label: DELETE_EMPLOYEE,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    affectedRequests: [GET_EMPLOYEES, GET_AUTHORIZED_EMPLOYEES],
    params: {
      new_owner_id: newOwnerId
    }
  });

export const getCurrentEmployee = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/employees`,
    method: "GET",
    onSuccess: onSuccessGetCurrentEmployee,
    label: GET_CURRENT_EMPLOYEE,
    ttl: HALF_HOUR,
    hash: hashParams(organizationId),
    params: {
      current_only: true
    }
  });

export const getOrganizationExpenses = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/pool_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_ORGANIZATION_EXPENSES),
    label: GET_ORGANIZATION_EXPENSES,
    ttl: MINUTE,
    hash: hashParams(organizationId)
  });

export const getRawExpenses = (resourceId, params) =>
  apiAction({
    url: `${API_URL}/resources/${resourceId}/raw_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_RAW_EXPENSES),
    label: GET_RAW_EXPENSES,
    ttl: 5 * MINUTE,
    hash: hashParams({ ...params, resourceId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getCleanExpenses = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/clean_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_CLEAN_EXPENSES),
    label: GET_CLEAN_EXPENSES,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getExpensesSummary = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/summary_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_EXPENSES_SUMMARY),
    label: GET_EXPENSES_SUMMARY,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getAvailableFilters = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/available_filters`,
    method: "GET",
    onSuccess: handleSuccess(SET_AVAILABLE_FILTERS),
    label: GET_AVAILABLE_FILTERS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getResourceCountBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/resources_count`,
    method: "GET",
    onSuccess: handleSuccess(SET_RESOURCE_COUNT_BREAKDOWN),
    label: GET_RESOURCE_COUNT_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getTagsBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/breakdown_tags`,
    method: "GET",
    onSuccess: handleSuccess(SET_TAGS_BREAKDOWN),
    label: GET_TAGS_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getRegionExpenses = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/region_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_REGION_EXPENSES),
    label: GET_REGION_EXPENSES,
    ttl: MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getTrafficExpenses = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/traffic_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_TRAFFIC_EXPENSES),
    label: GET_TRAFFIC_EXPENSES,
    ttl: 5 * MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      _id: params.resourceId
    }
  });

export const getAssignmentRules = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/rules`,
    method: "GET",
    onSuccess: handleSuccess(SET_ASSIGNMENT_RULES),
    label: GET_ASSIGNMENT_RULES,
    ttl: MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      pool_id: params.poolId,
      owner_id: params.ownerId
    }
  });

export const getK8sRightsizing = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/k8s_rightsizing`,
    method: "GET",
    onSuccess: handleSuccess(SET_K8S_RIGHTSIZING),
    label: GET_K8S_RIGHTSIZING,
    ttl: 5 * MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const updateAssignmentRulePriority = (assignmentRuleId, action) =>
  apiAction({
    url: `${API_URL}/rules/${assignmentRuleId}/priority`,
    method: "PATCH",
    onSuccess: onSuccessUpdateAssignmentRulePriority,
    label: UPDATE_ASSIGNMENT_RULE_PRIORITY,
    params: {
      action
    }
  });

export const getAssignmentRule = (assignmentRuleId) =>
  apiAction({
    url: `${API_URL}/rules/${assignmentRuleId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_ASSIGNMENT_RULE),
    label: GET_ASSIGNMENT_RULE
  });

export const createAssignmentRule = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/rules`,
    method: "POST",
    label: CREATE_ASSIGNMENT_RULE,
    affectedRequests: [GET_ASSIGNMENT_RULES],
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    params: {
      name: params.name,
      active: params.active,
      pool_id: params.poolId,
      owner_id: params.ownerId,
      conditions: params.conditions
    }
  });

export const updateAssignmentRule = (assignmentRuleId, params = {}) =>
  apiAction({
    url: `${API_URL}/rules/${assignmentRuleId}`,
    method: "PATCH",
    label: UPDATE_ASSIGNMENT_RULE,
    affectedRequests: [GET_ASSIGNMENT_RULES],
    params: {
      active: params.active,
      name: params.name,
      conditions: params.conditions,
      pool_id: params.poolId,
      owner_id: params.ownerId
    }
  });

export const deleteAssignmentRule = (ruleId) =>
  apiAction({
    url: `${API_URL}/rules/${ruleId}`,
    method: "DELETE",
    label: DELETE_ASSIGNMENT_RULE,
    affectedRequests: [GET_ASSIGNMENT_RULES]
  });

export const getResource = (resourceId, details = false) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_RESOURCE),
    label: GET_RESOURCE,
    ttl: 5 * MINUTE,
    hash: hashParams({ resourceId, details }),
    params: {
      details
    }
  });

export const getPoolPolicies = (poolId) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/policies`,
    method: "GET",
    onSuccess: handleSuccess(SET_POOL_POLICIES),
    label: GET_POOL_POLICIES,
    ttl: MINUTE,
    hash: hashParams({ poolId })
  });

const createPoolPolicyBase = ({ poolId, params, onSuccess, label, affectedRequests = [] }) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/policies`,
    method: "POST",
    label,
    onSuccess,
    params: {
      active: true,
      limit: params.limit,
      type: params.type
    },
    affectedRequests: [GET_GLOBAL_POOL_POLICIES, ...affectedRequests]
  });

export const createGlobalPoolPolicy = (poolId, params) =>
  createPoolPolicyBase({
    poolId,
    params,
    label: CREATE_GLOBAL_POOL_POLICY,
    affectedRequests: [GET_POOL_POLICIES]
  });

export const createPoolPolicy = (poolId, params) =>
  createPoolPolicyBase({
    poolId,
    params,
    onSuccess: onSuccessCreatePoolPolicy,
    label: CREATE_POOL_POLICY,
    affectedRequests: [GET_POOL]
  });

export const createExpensesExport = (poolId) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/expenses_export`,
    method: "POST",
    onSuccess: onSuccessExportLinkChange,
    label: CREATE_POOL_EXPENSES_EXPORT,
    affectedRequests: [GET_POOL]
  });

export const deleteExpensesExport = (poolId) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/expenses_export`,
    method: "DELETE",
    onSuccess: onSuccessExportLinkChange,
    label: DELETE_POOL_EXPENSES_EXPORT,
    affectedRequests: [GET_POOL]
  });

const updatePoolPolicyLimitBase = ({
  policyId,
  params,
  onSuccess,
  label,
  affectedRequests = [],
  allowMultipleRequests = false
}) =>
  apiAction({
    url: `${API_URL}/policies/${policyId}`,
    method: "PATCH",
    label,
    onSuccess,
    entityId: policyId,
    affectedRequests: [GET_RESOURCE, ...affectedRequests],
    params,
    allowMultipleRequests
  });

export const updatePoolPolicyLimit = (policyId, limit) =>
  updatePoolPolicyLimitBase({
    policyId,
    params: { limit },
    onSuccess: onSuccessCreatePoolPolicy,
    label: UPDATE_POOL_POLICY_LIMIT,
    affectedRequests: [GET_GLOBAL_POOL_POLICIES, GET_POOL]
  });

export const updateGlobalPoolPolicyLimit = (policyId, limit) =>
  updatePoolPolicyLimitBase({
    policyId,
    params: { limit },
    onSuccess: onSuccessUpdateGlobalPoolPolicyLimit,
    label: UPDATE_GLOBAL_POOL_POLICY_LIMIT,
    allowMultipleRequests: true,
    affectedRequests: [GET_POOL_POLICIES]
  });

const updatePoolPolicyActivityBase = ({
  policyId,
  params,
  affectedRequests = [],
  onSuccess,
  label,
  allowMultipleRequests = false
}) =>
  apiAction({
    url: `${API_URL}/policies/${policyId}`,
    method: "PATCH",
    label,
    onSuccess,
    entityId: policyId,
    affectedRequests: [GET_RESOURCE, GET_POOL, ...affectedRequests],
    params,
    allowMultipleRequests
  });

export const updatePoolPolicyActivity = (policyId, active) =>
  updatePoolPolicyActivityBase({
    policyId,
    params: { active },
    affectedRequests: [GET_GLOBAL_POOL_POLICIES],
    onSuccess: onSuccessCreatePoolPolicy,
    label: UPDATE_POOL_POLICY_ACTIVITY
  });

export const updateGlobalPoolPolicyActivity = (policyId, active) =>
  updatePoolPolicyActivityBase({
    policyId,
    params: { active },
    onSuccess: onSuccessUpdateGlobalPoolPolicyActivity,
    label: UPDATE_GLOBAL_POOL_POLICY_ACTIVITY,
    affectedRequests: [GET_POOL_POLICIES],
    allowMultipleRequests: true
  });

export const createResourceConstraint =
  (label) =>
  (resourceId, params = {}) =>
    apiAction({
      url: `${API_URL}/cloud_resources/${resourceId}/constraints`,
      method: "POST",
      label,
      onSuccess: onSuccessCreateResourceConstraint,
      params: {
        limit: params.limit,
        type: params.type
      }
    });

export const createTotalExpenseLimitResourceConstraint = (resourceId, limit) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}/constraints`,
    method: "POST",
    label: CREATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
    onSuccess: onSuccessCreateResourceConstraint,
    params: {
      limit,
      type: TOTAL_EXPENSE_LIMIT
    },
    affectedRequests: [GET_GLOBAL_RESOURCE_CONSTRAINTS]
  });

export const createDailyExpenseLimitResourceConstraint = (resourceId, limit) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}/constraints`,
    method: "POST",
    label: CREATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT,
    onSuccess: onSuccessCreateResourceConstraint,
    params: {
      limit,
      type: DAILY_EXPENSE_LIMIT
    },
    affectedRequests: [GET_GLOBAL_RESOURCE_CONSTRAINTS]
  });

export const createTtlResourceConstraint = (resourceId, limit) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}/constraints`,
    method: "POST",
    label: CREATE_TTL_RESOURCE_CONSTRAINT,
    onSuccess: onSuccessCreateResourceConstraint,
    params: {
      limit,
      type: TTL
    },
    affectedRequests: [GET_GLOBAL_RESOURCE_CONSTRAINTS]
  });

export const updateGlobalResourceConstraintLimit = (constraintId, limit) =>
  apiAction({
    url: `${API_URL}/constraints/${constraintId}`,
    method: "PATCH",
    label: UPDATE_GLOBAL_RESOURCE_CONSTRAINT_LIMIT,
    onSuccess: onSuccessUpdateGlobalResourceConstraintLimit,
    params: {
      limit
    },
    affectedRequests: [GET_RESOURCE],
    allowMultipleRequests: true
  });

const updateResourceConstraint = (label) => (constraintId, limit) =>
  apiAction({
    url: `${API_URL}/constraints/${constraintId}`,
    method: "PATCH",
    label,
    onSuccess: onSuccessCreateResourceConstraint,
    params: {
      limit
    },
    affectedRequests: [GET_GLOBAL_RESOURCE_CONSTRAINTS]
  });

export const updateTtlResourceConstraint = updateResourceConstraint(UPDATE_TTL_RESOURCE_CONSTRAINT);

export const updateTotalExpenseLimitResourceConstraint = updateResourceConstraint(
  UPDATE_TOTAL_EXPENSE_LIMIT_RESOURCE_CONSTRAINT
);

export const updateDailyExpenseLimitResourceConstraint = updateResourceConstraint(
  UPDATE_DAILY_EXPENSE_LIMIT_RESOURCE_CONSTRAINT
);

const deleteResourceConstraintBase = ({ constraintId, onSuccess, label, affectedRequests }) =>
  apiAction({
    url: `${API_URL}/constraints/${constraintId}`,
    method: "DELETE",
    onSuccess,
    entityId: constraintId,
    label,
    affectedRequests
  });

export const deleteResourceConstraint = (constraintId) =>
  deleteResourceConstraintBase({
    constraintId,
    onSuccess: () => onSuccessDeleteResourceConstraint(constraintId),
    label: DELETE_RESOURCE_CONSTRAINT
  });

export const deleteGlobalResourceConstraint = (constraintId) =>
  deleteResourceConstraintBase({
    constraintId,
    label: DELETE_GLOBAL_RESOURCE_CONSTRAINT,
    affectedRequests: [GET_GLOBAL_RESOURCE_CONSTRAINTS]
  });

export const getResourceLimitHits = (resourceId) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}/limit_hits`,
    method: "GET",
    onSuccess: handleSuccess(SET_RESOURCE_LIMIT_HITS),
    label: GET_RESOURCE_LIMIT_HITS,
    ttl: MINUTE,
    hash: hashParams({ resourceId })
  });

export const getOptimizationDetails = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/optimizations`,
    method: "GET",
    onSuccess: onSuccessGetOptimizationDetails,
    label: GET_OPTIMIZATION_DETAILS,
    hash: hashParams({ organizationId, ...params }),
    ttl: 5 * MINUTE,
    params: {
      type: params.type,
      limit: params.limit,
      status: params.status,
      cloud_account_id: params.cloudAccountIds
    }
  });

export const getOptimizationsOverview = (organizationId, cloudAccountIds = []) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/optimizations`,
    method: "GET",
    onSuccess: onSuccessGetOptimizationsOverview,
    label: GET_OPTIMIZATIONS_OVERVIEW,
    hash: hashParams({ organizationId, cloudAccountIds }),
    ttl: 5 * MINUTE,
    params: {
      limit: 3,
      overview: true,
      cloud_account_id: cloudAccountIds
    }
  });

export const getOptimizationOptions = (organizationId, recommendationType) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/recommendation_${recommendationType}`,
    method: "GET",
    hash: hashParams({
      organizationId,
      recommendationType
    }),
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_OPTIMIZATION_OPTIONS),
    label: GET_OPTIMIZATION_OPTIONS
  });

export const updateOptimizationOptions = (settingType, pathParams, params) => {
  const { organizationId, recommendationType } = pathParams;

  return apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/recommendation_${recommendationType}`,
    method: "PATCH",
    affectedRequests: [GET_OPTIMIZATIONS, GET_OPTIMIZATIONS_OVERVIEW, GET_ORGANIZATION_OPTIONS],
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    successHandlerPayload: {
      settingType
    },
    label: UPDATE_OPTIMIZATION_OPTIONS,
    params
  });
};

export const updateOptimizations = (checklistId, params) =>
  apiAction({
    url: `${API_URL}/checklists/${checklistId}`,
    method: "PATCH",
    label: UPDATE_OPTIMIZATIONS,
    onSuccess: onSuccessUpdateOptimizations,
    affectedRequests: [GET_OPTIMIZATIONS_OVERVIEW],
    params: {
      next_run: params.nextRun
    }
  });

export const getLiveDemo = () =>
  apiAction({
    url: `${API_URL}/live_demo`,
    method: "GET",
    onSuccess: handleSuccess(SET_LIVE_DEMO),
    label: GET_LIVE_DEMO,
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL
  });

export const createLiveDemo = ({ email, subscribeToNewsletter }) =>
  apiAction({
    url: `${API_URL}/live_demo`,
    method: "POST",
    onSuccess: onSuccessCreateLiveDemo,
    label: CREATE_LIVE_DEMO,
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL,
    params: {
      email,
      subscribe: subscribeToNewsletter
    }
  });

export const getTtlAnalysis = (poolId, params) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}/ttl_analysis`,
    method: "GET",
    onSuccess: handleSuccess(SET_TTL_ANALYSIS),
    label: GET_TTL_ANALYSIS,
    params: {
      start_date: params.startDate,
      end_date: params.endDate,
      ttl: params.ttl
    }
  });

export const applyAssignmentRules = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/rules_apply`,
    method: "POST",
    label: APPLY_ASSIGNMENT_RULES,
    params: {
      pool_id: params.poolId,
      include_children: params.includeChildren
    }
  });

export const updateResourceVisibility = (resourceId, params = {}) =>
  apiAction({
    url: `${API_URL}/resources/${resourceId}/optimizations`,
    method: "PATCH",
    label: UPDATE_RESOURCE_VISIBILITY,
    affectedRequests: [
      GET_RESOURCE,
      GET_ML_OPTIMIZATION_DETAILS,
      GET_ML_TASK_RECOMMENDATIONS,
      GET_OPTIMIZATION_DETAILS,
      GET_OPTIMIZATIONS_OVERVIEW
    ],
    params: {
      action: params.action,
      recommendation: params.recommendation
    }
  });

export const getFinOpsChecklist = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/finops_checklist`,
    method: "GET",
    onSuccess: handleSuccess(SET_FINOPS_CHECKLIST),
    ttl: HALF_HOUR,
    hash: hashParams(organizationId),
    label: GET_FINOPS_CHECKLIST
  });

export const updateFinOpsChecklist = (organizationId, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/finops_checklist`,
    method: "PATCH",
    label: UPDATE_FINOPS_CHECKLIST,
    onSuccess: onFinOpsChecklist,
    params: {
      value: JSON.stringify(value)
    }
  });

export const getRecommendationsDownloadLimit = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/recommendations_download_options`,
    method: "GET",
    onSuccess: handleSuccess(SET_RECOMMENDATIONS_DOWNLOAD_OPTIONS),
    ttl: HOUR,
    hash: hashParams(organizationId),
    label: GET_RECOMMENDATIONS_DOWNLOAD_OPTIONS
  });

export const getClusterTypes = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cluster_types`,
    method: "GET",
    onSuccess: handleSuccess(SET_CLUSTER_TYPES),
    label: GET_CLUSTER_TYPES,
    ttl: MINUTE,
    hash: hashParams(organizationId)
  });

export const createClusterType = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cluster_types`,
    method: "POST",
    label: CREATE_CLUSTER_TYPE,
    affectedRequests: [GET_CLUSTER_TYPES, GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: {
      name: params.name,
      tag_key: params.tagKey
    }
  });

export const deleteClusterType = (clusterTypeId) =>
  apiAction({
    url: `${API_URL}/cluster_types/${clusterTypeId}`,
    method: "DELETE",
    label: DELETE_CLUSTER_TYPE,
    affectedRequests: [GET_CLUSTER_TYPES, GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN]
  });

export const updateClusterTypePriority = (clusterTypeId, action) =>
  apiAction({
    url: `${API_URL}/cluster_types/${clusterTypeId}/priority`,
    method: "PATCH",
    label: UPDATE_CLUSTER_TYPE_PRIORITY,
    affectedRequests: [GET_CLUSTER_TYPES, GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: {
      action
    }
  });

export const applyClusterTypes = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cluster_types_apply`,
    method: "POST",
    label: APPLY_CLUSTER_TYPES,
    affectedRequests: [GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN, GET_AVAILABLE_FILTERS],
    params: {}
  });

export const getEnvironments = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/shareable_resources`,
    method: "GET",
    onSuccess: handleSuccess(SET_ENVIRONMENTS),
    label: GET_ENVIRONMENTS,
    ttl: MINUTE,
    hash: hashParams(organizationId)
  });

export const createEnvironment = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/environment_resources`,
    method: "POST",
    label: CREATE_ENVIRONMENT,
    affectedRequests: [GET_ENVIRONMENTS, GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: {
      name: params.name,
      resource_type: params.resourceType,
      tags: {},
      env_properties: params.properties,
      ssh_only: params.requireSshKey
    }
  });

export const deleteEnvironment = (environmentId) =>
  apiAction({
    url: `${API_URL}/environment_resources/${environmentId}`,
    method: "DELETE",
    label: DELETE_ENVIRONMENT,
    affectedRequests: [
      GET_ENVIRONMENTS,
      GET_CLEAN_EXPENSES,
      GET_EXPENSES_SUMMARY,
      GET_EXPENSES_DAILY_BREAKDOWN,
      GET_RESOURCE_COUNT_BREAKDOWN
    ]
  });

export const updateEnvironmentActivity = (environmentId, isActive) =>
  apiAction({
    url: `${API_URL}/environment_resources/${environmentId}`,
    method: "PATCH",
    label: UPDATE_ENVIRONMENT_ACTIVITY,
    entityId: environmentId,
    affectedRequests: [
      GET_ENVIRONMENTS,
      GET_CLEAN_EXPENSES,
      GET_EXPENSES_DAILY_BREAKDOWN,
      GET_RESOURCE_COUNT_BREAKDOWN,
      GET_RESOURCE
    ],
    params: { active: isActive }
  });

export const updateEnvironmentSshRequirement = (environmentId, requireSshKey) =>
  apiAction({
    url: `${API_URL}/environment_resources/${environmentId}`,
    method: "PATCH",
    label: UPDATE_ENVIRONMENT_SSH_REQUIREMENT,
    onSuccess: onSuccessUpdateEnvironmentSshRequirement,
    entityId: environmentId,
    affectedRequests: [GET_ENVIRONMENTS, GET_CLEAN_EXPENSES, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: { ssh_only: requireSshKey }
  });

export const updateEnvironmentProperty = (environmentId, { propertyName, propertyValue }) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${environmentId}`,
    method: "PATCH",
    onSuccess: onSuccessUpdateEnvironmentProperty,
    allowMultipleRequests: true,
    label: UPDATE_ENVIRONMENT_PROPERTY,
    entityId: propertyName,
    affectedRequests: [GET_ENVIRONMENTS],
    params: { env_properties: { [propertyName]: propertyValue } }
  });

export const getDataSourceNodes = (cloudAccountId) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${cloudAccountId}/nodes`,
    method: "GET",
    label: GET_DATA_SOURCE_NODES,
    ttl: MINUTE,
    hash: hashParams(cloudAccountId),
    onSuccess: handleSuccess(SET_DATA_SOURCE_NODES)
  });

export const getResourceMetrics = (resourceId, params = {}) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}/metrics`,
    method: "GET",
    label: GET_RESOURCE_METRICS,
    ttl: MINUTE,
    hash: hashParams({ ...params, resourceId }),
    onSuccess: handleSuccess(SET_RESOURCE_METRICS),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getResourceCostModel = (resourceId) =>
  apiAction({
    url: `${API_URL}/resource_cost_models/${resourceId}`,
    method: "GET",
    label: GET_RESOURCE_COST_MODEL,
    ttl: MINUTE,
    hash: hashParams(resourceId),
    onSuccess: handleSuccess(SET_RESOURCE_COST_MODEL)
  });

export const updateResourceCostModel = (resourceId, params) =>
  apiAction({
    url: `${API_URL}/resource_cost_models/${resourceId}`,
    method: "PATCH",
    label: UPDATE_RESOURCE_COST_MODEL,
    affectedRequests: [GET_RESOURCE_COST_MODEL],
    params: {
      value: { hourly_cost: params.hourlyPrice }
    }
  });

export const getDataSourceSkus = (dataSourceId) =>
  apiAction({
    url: `${API_URL}/sku_cost_models/${dataSourceId}`,
    method: "GET",
    label: GET_DATASOURCE_SKUS,
    ttl: 30 * MINUTE,
    hash: hashParams(dataSourceId),
    onSuccess: handleSuccess(SET_DATASOURCE_SKUS),
    params: {
      details: true
    }
  });

export const updateDataSourceSku = (dataSourceId, value) =>
  apiAction({
    url: `${API_URL}/sku_cost_models/${dataSourceId}`,
    method: "PATCH",
    label: UPDATE_DATASOURCE_SKU,
    affectedRequests: [GET_DATASOURCE_SKUS],
    params: {
      value
    }
  });

export const markResourcesAsEnvironments = (organizationId, resourceIds) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/shareable/bulk`,
    method: "POST",
    label: MARK_RESOURCES_AS_ENVIRONMENTS,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    affectedRequests: [GET_CLEAN_EXPENSES, GET_ENVIRONMENTS, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: {
      resource_ids: resourceIds
    }
  });

export const getEnvironmentBookings = (resourceId) =>
  apiAction({
    url: `${API_URL}/shareable/${resourceId}/bookings`,
    method: "GET",
    label: GET_ENVIRONMENT_BOOKINGS,
    ttl: 5 * MINUTE,
    hash: hashParams(resourceId),
    onSuccess: handleSuccess(SET_ENVIRONMENT_BOOKINGS)
  });

export const updateBooking = (bookingId, { releasedAt }) =>
  apiAction({
    url: `${API_URL}/shareable/${bookingId}`,
    method: "PATCH",
    label: UPDATE_BOOKING,
    affectedRequests: [GET_CLEAN_EXPENSES, GET_ENVIRONMENTS, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN],
    params: {
      released_at: releasedAt
    }
  });

export const deleteBooking = (bookingId) =>
  apiAction({
    url: `${API_URL}/shareable/${bookingId}`,
    method: "DELETE",
    label: DELETE_BOOKING,
    affectedRequests: [GET_CLEAN_EXPENSES, GET_ENVIRONMENTS, GET_EXPENSES_DAILY_BREAKDOWN, GET_RESOURCE_COUNT_BREAKDOWN]
  });

// More params supported, add if required, see Swagger
export const getWebhooks = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/webhooks`,
    method: "GET",
    label: GET_WEBHOOKS,
    ttl: 5 * MINUTE,
    hash: hashParams({ ...params, organizationId }),
    onSuccess: handleSuccess(SET_WEBHOOKS),
    params: {
      object_id: params.objectId,
      object_type: params.objectType
    }
  });

// More params supported, add if required, see Swagger
export const createWebhook = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/webhooks`,
    label: CREATE_WEBHOOK,
    onSuccess: onSuccessCreateWebhook,
    params: {
      object_type: params.objectType,
      object_id: params.objectId,
      action: params.action,
      url: params.url
    }
  });

// More params supported, add if required, see Swagger
export const updateWebhook = (webhookId, params) =>
  apiAction({
    url: `${API_URL}/webhooks/${webhookId}`,
    method: "PATCH",
    label: UPDATE_WEBHOOK,
    onSuccess: onSuccessUpdateWebhook,
    params: {
      url: params.url,
      active: params.active
    }
  });

export const deleteWebhook = (webhookId) =>
  apiAction({
    url: `${API_URL}/webhooks/${webhookId}`,
    method: "DELETE",
    label: DELETE_WEBHOOK,
    onSuccess: onSuccessDeleteWebhook(webhookId)
  });

export const getSshKeys = (employeeId) =>
  apiAction({
    url: `${API_URL}/employees/${employeeId}/ssh_keys`,
    method: "GET",
    label: GET_SSH_KEYS,
    ttl: 5 * MINUTE,
    hash: hashParams(employeeId),
    onSuccess: handleSuccess(SET_SSH_KEYS)
  });

export const createSshKey = (employeeId, params) =>
  apiAction({
    url: `${API_URL}/employees/${employeeId}/ssh_keys`,
    label: CREATE_SSH_KEY,
    params: {
      name: params.name,
      key: params.key
    },
    onSuccess: onSuccessCreateSshKey
  });

export const updateSshKey = (sshKeyId, params) =>
  apiAction({
    url: `${API_URL}/ssh_keys/${sshKeyId}`,
    method: "PATCH",
    label: UPDATE_SSH_KEY,
    affectedRequests: [GET_EMPLOYEES],
    params: {
      name: params.name,
      default: params.default
    },
    onSuccess: onSuccessUpdateSshKey
  });

export const deleteSshKey = (sshKeyId) =>
  apiAction({
    url: `${API_URL}/ssh_keys/${sshKeyId}`,
    method: "DELETE",
    label: DELETE_SSH_KEY,
    affectedRequests: [GET_SSH_KEYS]
  });

export const updateResource = (resourceId, { shareable }) =>
  apiAction({
    url: `${API_URL}/cloud_resources/${resourceId}`,
    method: "PATCH",
    label: UPDATE_RESOURCE,
    affectedRequests: [GET_RESOURCE, GET_ENVIRONMENTS],
    params: {
      shareable
    }
  });

export const bookEnvironment = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/shareable_book`,
    method: "POST",
    label: BOOK_ENVIRONMENT,
    affectedRequests: [GET_ENVIRONMENTS, GET_ENVIRONMENT_BOOKINGS],
    params: {
      resource_id: params.resourceId,
      acquired_by_id: params.bookedBy,
      acquired_since: params.bookSince,
      released_at: params.bookUntil,
      ssh_key_id: params.sshKeyId
    }
  });

export const getOrganizationCalendar = (organizationId) =>
  apiAction({
    url: `${API_URL}/organization_calendars/${organizationId}`,
    method: "GET",
    label: GET_ORGANIZATION_CALENDAR,
    ttl: MINUTE * 10,
    hash: hashParams(organizationId),
    onSuccess: handleSuccess(SET_ORGANIZATION_CALENDAR)
  });

export const calendarSynchronization = (organizationId, calendarId) =>
  apiAction({
    url: `${API_URL}/calendar_synchronizations`,
    method: "POST",
    label: CALENDAR_SYNCHRONIZATION,
    affectedRequests: [GET_ORGANIZATION_CALENDAR],
    params: {
      organization_id: organizationId,
      calendar_id: calendarId
    }
  });

export const deleteCalendarSynchronization = (id) =>
  apiAction({
    url: `${API_URL}/calendar_synchronizations/${id}`,
    method: "DELETE",
    label: DELETE_CALENDAR_SYNCHRONIZATION,
    affectedRequests: [GET_ORGANIZATION_CALENDAR]
  });

export const getDailyExpensesBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/breakdown_expenses`,
    method: "GET",
    onSuccess: handleSuccess(SET_EXPENSES_DAILY_BREAKDOWN),
    label: GET_EXPENSES_DAILY_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params
  });

export const getOrganizationLimitHits = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/organization_limit_hits`,
    method: "GET",
    label: GET_ORGANIZATION_LIMIT_HITS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_ORGANIZATION_LIMIT_HITS),
    params: {
      constraint_id: params.constraintId
    }
  });

export const getGlobalPoolPolicies = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/resource_policies`,
    method: "GET",
    label: GET_GLOBAL_POOL_POLICIES,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_GLOBAL_POOL_POLICIES),
    params
  });

export const getGlobalResourceConstraints = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/resource_constraints`,
    method: "GET",
    label: GET_GLOBAL_RESOURCE_CONSTRAINTS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_GLOBAL_RESOURCE_CONSTRAINTS),
    params
  });

export const getArchivedOptimizationsCount = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/archived_recommendations_count`,
    method: "GET",
    label: GET_ARCHIVED_OPTIMIZATIONS_COUNT,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_ARCHIVED_OPTIMIZATIONS_COUNT),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getArchivedOptimizationsBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/breakdown_archived_recommendations`,
    method: "GET",
    label: GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN),
    params: {
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getArchivedOptimizationDetails = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/archived_recommendations_details`,
    method: "GET",
    label: GET_ARCHIVED_OPTIMIZATION_DETAILS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_ARCHIVED_OPTIMIZATION_DETAILS),
    params: {
      archived_at: params.archivedAt,
      reason: params.reason,
      type: params.type,
      limit: params.limit
    }
  });

export const getMlTasks = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASKS),
    hash: hashParams(organizationId),
    label: GET_ML_TASKS
  });

export const getMlLeaderboards = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/leaderboard`,
    method: "GET",
    ttl: 30 * MINUTE,
    onSuccess: handleSuccess(SET_ML_LEADERBOARD),
    hash: hashParams({ organizationId, taskId }),
    label: GET_ML_LEADERBOARD
  });

export const createMlLeaderboard = (organizationId, taskId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/leaderboard`,
    method: "POST",
    label: CREATE_ML_LEADERBOARD,
    affectedRequests: [GET_ML_LEADERBOARD],
    params: {
      filters: params.filters,
      group_by_hp: params.groupByHyperparameters,
      grouping_tags: params.groupingTags,
      other_metrics: params.otherMetrics,
      primary_metric: params.primaryMetric,
      dataset_coverage_rules: params.datasetCoverageRules
    }
  });

export const updateMlLeaderboard = (organizationId, taskId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/leaderboard`,
    method: "PATCH",
    label: UPDATE_ML_LEADERBOARD,
    affectedRequests: [GET_ML_LEADERBOARD_DATASET_DETAILS, GET_ML_LEADERBOARD],
    params: {
      filters: params.filters,
      group_by_hp: params.groupByHyperparameters,
      grouping_tags: params.groupingTags,
      other_metrics: params.otherMetrics,
      primary_metric: params.primaryMetric,
      dataset_coverage_rules: params.datasetCoverageRules
    }
  });

export const getMlLeaderboardDatasets = (organizationId, leaderboardId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboards/${leaderboardId}/leaderboard_datasets`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_LEADERBOARD_DATASETS),
    hash: hashParams({ organizationId, leaderboardId }),
    label: GET_ML_LEADERBOARD_DATASETS
  });

export const getMlLeaderboardDataset = (organizationId, leaderboardDatasetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboard_datasets/${leaderboardDatasetId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_LEADERBOARD_DATASET),
    hash: hashParams({ organizationId, leaderboardDatasetId }),
    label: GET_ML_LEADERBOARD_DATASET
  });

export const createMlLeaderboardDataset = (organizationId, leaderboardId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboards/${leaderboardId}/leaderboard_datasets`,
    method: "POST",
    label: CREATE_ML_LEADERBOARD_DATASET,
    affectedRequests: [GET_ML_LEADERBOARD],
    params: {
      name: params.name,
      dataset_ids: params.datasetIds,
      filters: params.filters,
      group_by_hp: params.groupByHyperparameters,
      grouping_tags: params.groupingTags,
      other_metrics: params.otherMetrics,
      primary_metric: params.primaryMetric,
      dataset_coverage_rules: params.datasetCoverageRules
    }
  });

export const updateMlLeaderboardDataset = (organizationId, leaderboardDatasetId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboard_datasets/${leaderboardDatasetId}`,
    method: "PATCH",
    label: UPDATE_ML_LEADERBOARD_DATASET,
    onSuccess: onUpdateMlLeaderboardDataset,
    affectedRequests: [GET_ML_LEADERBOARD],
    params: {
      name: params.name,
      dataset_ids: params.datasetIds,
      filters: params.filters,
      group_by_hp: params.groupByHyperparameters,
      grouping_tags: params.groupingTags,
      other_metrics: params.otherMetrics,
      primary_metric: params.primaryMetric,
      dataset_coverage_rules: params.datasetCoverageRules
    }
  });

export const deleteMlLeaderboardDataset = (organizationId, leaderboardDatasetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboard_datasets/${leaderboardDatasetId}`,
    method: "DELETE",
    label: DELETE_ML_LEADERBOARD_DATASET,
    affectedRequests: [GET_ML_LEADERBOARD]
  });

export const getMlLeaderboardDatasetInfo = (organizationId, leaderboardDatasetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/leaderboard_datasets/${leaderboardDatasetId}/generate`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_LEADERBOARD_DATASET_DETAILS),
    hash: hashParams({ organizationId, leaderboardDatasetId }),
    label: GET_ML_LEADERBOARD_DATASET_DETAILS
  });

export const getMlDatasets = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/datasets`,
    method: "GET",
    ttl: 30 * MINUTE,
    onSuccess: handleSuccess(SET_ML_DATASETS),
    hash: hashParams(organizationId),
    label: GET_ML_DATASETS
  });

export const getMlDataset = (organizationId, datasetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/datasets/${datasetId}`,
    method: "GET",
    ttl: 30 * MINUTE,
    onSuccess: handleSuccess(SET_ML_DATASET),
    hash: hashParams(organizationId, datasetId),
    label: GET_ML_DATASET
  });

export const getMlDatasetLabels = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/labels`,
    method: "GET",
    ttl: 30 * MINUTE,
    onSuccess: handleSuccess(SET_ML_DATASET_LABELS),
    hash: hashParams(organizationId),
    label: GET_ML_DATASET_LABELS
  });

export const createMlDataset = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/datasets`,
    method: "POST",
    label: CREATE_ML_DATASET,
    params,
    affectedRequests: [GET_ML_DATASETS]
  });

export const updateMlDataset = (organizationId, datasetId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/datasets/${datasetId}`,
    method: "PATCH",
    label: UPDATE_ML_DATASET,
    params,
    affectedRequests: [GET_ML_DATASET, GET_ML_DATASETS]
  });

export const deleteMlDataset = (organizationId, datasetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/datasets/${datasetId}`,
    method: "DELETE",
    label: DELETE_ML_DATASET,
    affectedRequests: [GET_ML_DATASETS]
  });

export const getMlTaskRecommendations = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/optimizations`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASK_RECOMMENDATIONS),
    hash: hashParams({ organizationId, taskId }),
    label: GET_ML_TASK_RECOMMENDATIONS
  });

export const getMlTaskRecommendationDetails = (organizationId, taskId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/optimizations`,
    method: "GET",
    onSuccess: onSuccessGetMLOptimizationDetails,
    label: GET_ML_OPTIMIZATION_DETAILS,
    hash: hashParams({ organizationId, taskId, ...params }),
    ttl: 5 * MINUTE,
    params: {
      type: params.type,
      status: params.status
    }
  });

export const getMlTask = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASK),
    hash: hashParams({ organizationId, taskId }),
    label: GET_ML_TASK
  });

export const getMlTaskRuns = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/runs`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASK_RUNS),
    hash: hashParams({ organizationId, taskId }),
    label: GET_ML_TASK_RUNS
  });

export const getMlTaskRunsBulk = (organizationId, taskId, runIds) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/runs/bulk`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASK_RUNS_BULK),
    hash: hashParams({ organizationId, taskId, runIds }),
    label: GET_ML_TASK_RUNS_BULK,
    params: {
      run_id: runIds
    }
  });

export const getMlRunDetails = (organizationId, runId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runs/${runId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_RUN_DETAILS),
    hash: hashParams({ organizationId, runId }),
    label: GET_ML_RUN_DETAILS
  });

export const getMlRunDetailsBreakdown = (organizationId, runId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runs/${runId}/breakdown`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_RUN_DETAILS_BREAKDOWN),
    hash: hashParams({ organizationId, runId }),
    label: GET_ML_RUN_DETAILS_BREAKDOWN
  });

export const createMlTask = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks`,
    method: "POST",
    label: CREATE_ML_TASK,
    params,
    affectedRequests: [GET_ML_TASKS]
  });

export const updateMlTask = (organizationId, taskId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}`,
    method: "PATCH",
    label: UPDATE_ML_TASK,
    onSuccess: onUpdateMlTask,
    params,
    affectedRequests: [GET_ML_TASKS]
  });

export const deleteMlTask = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}`,
    method: "DELETE",
    label: DELETE_ML_TASK,
    affectedRequests: [GET_ML_TASKS]
  });

export const getMlTaskModelVersions = (organizationId, taskId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/tasks/${taskId}/model_versions`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_TASK_MODEL_VERSIONS),
    label: GET_ML_TASK_MODEL_VERSIONS
  });

export const getMlModels = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/models`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_MODELS),
    hash: hashParams(organizationId),
    label: GET_ML_MODELS
  });

export const getMlModel = (organizationId, modelId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/models/${modelId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_MODEL),
    hash: hashParams({ organizationId, modelId }),
    label: GET_ML_MODEL
  });

export const createMlModel = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/models`,
    method: "POST",
    label: CREATE_ML_MODEL,
    params,
    affectedRequests: [GET_ML_MODELS]
  });

export const updateMlModel = (organizationId, modelId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/models/${modelId}`,
    method: "PATCH",
    label: UPDATE_ML_MODEL,
    onSuccess: onUpdateMlModel,
    params,
    affectedRequests: [GET_ML_MODELS]
  });

export const deleteMlModel = (organizationId, modelId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/models/${modelId}`,
    method: "DELETE",
    label: DELETE_ML_MODEL,
    affectedRequests: [GET_ML_MODELS]
  });

// eslint-disable-next-line max-params
export const updateMlModelVersion = (organizationId, modelId, runId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runs/${runId}/models/${modelId}/version`,
    method: "PATCH",
    label: UPDATE_ML_MODEL_VERSION,
    params,
    affectedRequests: [GET_ML_MODEL, GET_ML_MODELS]
  });

export const getMlGlobalMetrics = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/metrics`,
    method: "GET",
    label: GET_ML_GLOBAL_METRICS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId }),
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL,
    onSuccess: handleSuccess(SET_ML_GLOBAL_METRICS)
  });

export const getMlGlobalMetric = (organizationId, metricId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/metrics/${metricId}`,
    method: "GET",
    label: GET_ML_GLOBAL_METRIC,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, metricId }),
    onSuccess: handleSuccess(SET_ML_GLOBAL_METRIC)
  });

export const createGlobalMetric = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/metrics`,
    method: "POST",
    label: CREATE_GLOBAL_METRIC,
    params,
    affectedRequests: [GET_ML_GLOBAL_METRICS]
  });

export const updateGlobalMetric = (organizationId, metricId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/metrics/${metricId}`,
    method: "PATCH",
    label: UPDATE_GLOBAL_METRIC,
    affectedRequests: [GET_ML_GLOBAL_METRICS],
    params
  });

export const deleteGlobalMetric = (organizationId, metricId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/metrics/${metricId}`,
    method: "DELETE",
    label: DELETE_GLOBAL_METRIC,
    affectedRequests: [GET_ML_GLOBAL_METRICS]
  });

export const getProfilingToken = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/profiling_token`,
    method: "GET",
    label: GET_PROFILING_TOKEN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId }),
    onSuccess: handleSuccess(SET_PROFILING_TOKEN)
  });

export const getMlExecutors = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/executors`,
    method: "GET",
    label: GET_ML_EXECUTORS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    onSuccess: handleSuccess(SET_ML_EXECUTORS),
    params: {
      task_id: params.taskIds,
      run_id: params.runIds
    }
  });

export const getMlExecutorsBreakdown = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/executors_breakdown`,
    method: "GET",
    onSuccess: handleSuccess(SET_ML_EXECUTORS_BREAKDOWN),
    label: GET_ML_EXECUTORS_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams(organizationId)
  });

export const getMlArtifacts = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/artifacts`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_ARTIFACTS),
    hash: hashParams({ organizationId, ...params }),
    label: GET_ML_ARTIFACTS,
    params: {
      limit: params.limit,
      run_id: params.runId,
      start_from: params.startFrom,
      text_like: params.textLike,
      created_at_gt: params.createdAtGt,
      created_at_lt: params.createdAtLt,
      task_id: params.taskId
    }
  });

export const getMlArtifact = (organizationId, artifactId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/artifacts/${artifactId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_ARTIFACT),
    hash: hashParams({ organizationId, artifactId }),
    label: GET_ML_ARTIFACT
  });

export const updateMlArtifact = (organizationId, artifactId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/artifacts/${artifactId}`,
    method: "PATCH",
    label: UPDATE_ML_ARTIFACT,
    onSuccess: onUpdateMlArtifact,
    params,
    affectedRequests: [GET_ML_ARTIFACTS]
  });

export const createMlArtifact = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/artifacts`,
    method: "POST",
    label: CREATE_ML_ARTIFACT,
    params: {
      name: params.name,
      path: params.path,
      description: params.description,
      tags: params.tags,
      run_id: params.runId
    },
    affectedRequests: [GET_ML_ARTIFACTS]
  });

export const deleteMlArtifact = (organizationId, artifactId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/artifacts/${artifactId}`,
    method: "DELETE",
    label: DELETE_ML_ARTIFACT,
    affectedRequests: [GET_ML_ARTIFACTS]
  });

export const getReservedInstancesBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/ri_breakdown`,
    method: "GET",
    onSuccess: handleSuccess(SET_RESERVED_INSTANCES_BREAKDOWN),
    label: GET_RESERVED_INSTANCES_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params: {
      cloud_account_id: params.dataSourceIds,
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getSavingPlansBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/sp_breakdown`,
    method: "GET",
    onSuccess: handleSuccess(SET_SAVING_PLANS_BREAKDOWN),
    label: GET_SAVING_PLANS_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    params: {
      cloud_account_id: params.dataSourceIds,
      start_date: params.startDate,
      end_date: params.endDate
    }
  });

export const getMlRunsetTemplates = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates_overview`,
    method: "GET",
    onSuccess: handleSuccess(SET_ML_RUNSET_TEMPLATES),
    hash: hashParams({ organizationId }),
    label: GET_ML_RUNSET_TEMPLATES,
    ttl: 5 * MINUTE
  });

export const getMlRunsetTemplate = (organizationId, runsetTemplateId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates/${runsetTemplateId}`,
    method: "GET",
    hash: hashParams({ organizationId, runsetTemplateId }),
    onSuccess: handleSuccess(SET_ML_RUNSET_TEMPLATE),
    label: GET_ML_RUNSET_TEMPLATE,
    ttl: 5 * MINUTE
  });

export const createMlRunsetTemplate = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates`,
    method: "POST",
    label: CREATE_ML_RUNSET_TEMPLATE,
    params,
    affectedRequests: [GET_ML_RUNSET_TEMPLATES]
  });

export const updateMlRunsetTemplate = (organizationId, runsetTemplateId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates/${runsetTemplateId}`,
    method: "PATCH",
    label: UPDATE_ML_RUNSET_TEMPLATE,
    onSuccess: onUpdateMlRunsetTemplate,
    params,
    affectedRequests: [GET_ML_RUNSET_TEMPLATES]
  });

export const deleteMlRunsetTemplate = (organizationId, runsetTemplateId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates/${runsetTemplateId}`,
    method: "DELETE",
    label: DELETE_ML_RUNSET_TEMPLATE,
    affectedRequests: [GET_ML_RUNSET_TEMPLATES]
  });

export const getMlRunsets = (organizationId, runsetTemplateId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates/${runsetTemplateId}/runsets`,
    method: "GET",
    hash: hashParams({ organizationId, runsetTemplateId }),
    onSuccess: handleSuccess(SET_ML_RUNSETS),
    label: GET_ML_RUNSETS,
    ttl: 5 * MINUTE
  });

export const getMlRunset = (organizationId, runsetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runsets/${runsetId}`,
    method: "GET",
    hash: hashParams({ organizationId, runsetId }),
    onSuccess: handleSuccess(SET_ML_RUNSET),
    label: GET_ML_RUNSET,
    ttl: 5 * MINUTE
  });

export const createMlRunset = (organizationId, runsetTemplateId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/templates/${runsetTemplateId}/runsets`,
    method: "POST",
    label: CREATE_ML_RUNSET,
    params,
    affectedRequests: [GET_ML_RUNSETS]
  });

export const stopMlRunset = (organizationId, runsetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runsets/${runsetId}`,
    method: "PATCH",
    label: STOP_ML_RUNSET,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    params: {
      action: "stop"
    },
    affectedRequests: [GET_ML_RUNSET, GET_ML_RUNSETS]
  });

export const getMlRunsetsRuns = (organizationId, runsetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runsets/${runsetId}/runs`,
    method: "GET",
    hash: hashParams({ organizationId, runsetId }),
    onSuccess: handleSuccess(SET_ML_RUNSETS_RUNS),
    label: GET_ML_RUNSETS_RUNS,
    ttl: 5 * MINUTE
  });

export const getMlRunsetExecutors = (organizationId, runsetId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/runsets/${runsetId}/runners`,
    method: "GET",
    hash: hashParams({ organizationId, runsetId }),
    onSuccess: handleSuccess(SET_ML_RUNSET_EXECUTORS),
    label: GET_ML_RUNSET_EXECUTORS,
    ttl: 5 * MINUTE
  });

export const getOrganizationBIExports = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/bi`,
    method: "GET",
    hash: hashParams({ organizationId }),
    onSuccess: handleSuccess(SET_ORGANIZATION_BI_EXPORTS),
    label: GET_ORGANIZATION_BI_EXPORT,
    ttl: 5 * MINUTE
  });

export const createOrganizationBIExports = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/bi`,
    method: "POST",
    label: CREATE_ORGANIZATION_BI_EXPORT,
    params,
    affectedRequests: [GET_ORGANIZATION_BI_EXPORT]
  });

export const getBIExport = (biExportId) =>
  apiAction({
    url: `${API_URL}/bi/${biExportId}`,
    method: "GET",
    hash: hashParams({ biExportId }),
    label: GET_BI_EXPORT,
    onSuccess: handleSuccess(SET_BI_EXPORT),
    ttl: 5 * MINUTE
  });

export const updateBIExport = (biExportId, params) =>
  apiAction({
    url: `${API_URL}/bi/${biExportId}`,
    method: "PATCH",
    label: UPDATE_BI_EXPORT,
    onSuccess: onUpdateBIExport,
    affectedRequests: [GET_ORGANIZATION_BI_EXPORT],
    params
  });

export const deleteBIExport = (biExportId) =>
  apiAction({
    url: `${API_URL}/bi/${biExportId}`,
    method: "DELETE",
    label: DELETE_BI_EXPORT,
    affectedRequests: [GET_ORGANIZATION_BI_EXPORT]
  });

export const getRelevantFlavors = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/relevant_flavors`,
    method: "GET",
    label: GET_RELEVANT_FLAVORS,
    onSuccess: handleSuccess(SET_RELEVANT_FLAVORS),
    hash: hashParams({ organizationId, params }),
    ttl: 5 * MINUTE,
    params
  });

export const getS3DuplicatesOrganizationSettings = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/s3_duplicates_settings`,
    method: "GET",
    ttl: HOUR,
    onSuccess: handleSuccess(SET_S3_DUPLICATES_ORGANIZATION_SETTINGS),
    hash: hashParams(organizationId),
    label: GET_S3_DUPLICATES_ORGANIZATION_SETTINGS
  });

export const updateS3DuplicatesOrganizationSettings = (organizationId, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/s3_duplicates_settings`,
    method: "PATCH",
    onSuccess: onUpdateS3DuplicatesOrganizationSettings,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    label: UPDATE_S3_DUPLICATES_ORGANIZATION_SETTINGS,
    affectedRequests: [GET_S3_DUPLICATES_ORGANIZATION_SETTINGS],
    params: {
      value: JSON.stringify(value)
    }
  });

export const getOrganizationCloudResources = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_resources`,
    method: "GET",
    hash: hashParams({ organizationId, params }),
    onSuccess: handleSuccess(SET_ORGANIZATION_CLOUD_RESOURCES),
    label: GET_ORGANIZATION_CLOUD_RESOURCES,
    ttl: 5 * MINUTE,
    params
  });

export const getOrganizationGeminis = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/geminis`,
    method: "GET",
    hash: hashParams({ organizationId }),
    onSuccess: handleSuccess(SET_ORGANIZATION_GEMINIS),
    label: GET_ORGANIZATION_GEMINIS,
    ttl: 5 * MINUTE
  });

export const getGemini = (checkId) =>
  apiAction({
    url: `${API_URL}/geminis/${checkId}`,
    method: "GET",
    hash: hashParams({ checkId }),
    onSuccess: handleSuccess(SET_GEMINI),
    label: GET_GEMINI,
    ttl: 5 * MINUTE
  });

export const createOrganizationGemini = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/geminis`,
    method: "POST",
    label: CREATE_ORGANIZATION_GEMINI,
    affectedRequests: [GET_ORGANIZATION_GEMINIS],
    params
  });

export const createSurvey = (organizationId, { type, payload }) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/disconnect_survey`,
    method: "POST",
    label: CREATE_SURVEY,
    params: {
      survey_type: type,
      payload
    }
  });

export const getPowerSchedules = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/power_schedules`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_POWER_SCHEDULES),
    hash: hashParams(organizationId),
    label: GET_POWER_SCHEDULES
  });

export const getPowerSchedule = (powerScheduleId) =>
  apiAction({
    url: `${API_URL}/power_schedules/${powerScheduleId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_POWER_SCHEDULE),
    hash: hashParams(powerScheduleId),
    label: GET_POWER_SCHEDULE
  });

export const createPowerSchedule = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/power_schedules`,
    method: "POST",
    label: CREATE_POWER_SCHEDULES,
    affectedRequests: [GET_POWER_SCHEDULES],
    params
  });

export const deletePowerSchedule = (powerScheduleId) =>
  apiAction({
    url: `${API_URL}/power_schedules/${powerScheduleId}`,
    method: "DELETE",
    label: DELETE_POWER_SCHEDULE,
    affectedRequests: [GET_POWER_SCHEDULES]
  });

export const updatePowerSchedule = (powerScheduleId, params) =>
  apiAction({
    url: `${API_URL}/power_schedules/${powerScheduleId}`,
    method: "PATCH",
    label: UPDATE_POWER_SCHEDULE,
    onSuccess: onUpdatePowerSchedule,
    entityId: powerScheduleId,
    affectedRequests: [GET_POWER_SCHEDULES],
    params
  });

export const attachInstancesToSchedule = (powerScheduleId, instancesToAttach) =>
  apiAction({
    url: `${API_URL}/power_schedules/${powerScheduleId}/actions`,
    method: "POST",
    label: ATTACH_INSTANCES_TO_SCHEDULE,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    affectedRequests: [GET_POWER_SCHEDULE, GET_POWER_SCHEDULES],
    params: {
      action: "attach",
      instance_id: instancesToAttach
    }
  });

export const removeInstancesFromSchedule = (powerScheduleId, instancesToRemove) =>
  apiAction({
    url: `${API_URL}/power_schedules/${powerScheduleId}/actions`,
    method: "POST",
    label: REMOVE_INSTANCES_FROM_SCHEDULE,
    successHandlerType: SUCCESS_HANDLER_TYPE_ALERT,
    affectedRequests: [GET_POWER_SCHEDULE, GET_POWER_SCHEDULES],
    params: {
      action: "detach",
      instance_id: instancesToRemove
    }
  });

export const getLayouts = (organizationId, { layoutType, entityId, includeShared }) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/layouts`,
    method: "GET",
    hash: hashParams({ organizationId, layoutType, entityId, includeShared }),
    onSuccess: handleSuccess(SET_LAYOUTS),
    label: GET_LAYOUTS,
    ttl: 5 * MINUTE,
    params: {
      type: layoutType,
      entity_id: entityId,
      include_shared: includeShared
    }
  });

export const getLayout = (organizationId, layoutId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/layouts/${layoutId}`,
    method: "GET",
    hash: hashParams({ organizationId, layoutId }),
    onSuccess: handleSuccess(SET_LAYOUT),
    entityId: layoutId,
    label: GET_LAYOUT,
    ttl: 5 * MINUTE
  });

export const createLayout = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/layouts`,
    method: "POST",
    label: CREATE_LAYOUT,
    affectedRequests: [GET_LAYOUTS],
    onSuccess: handleSuccess(CREATE_LAYOUT),
    params: {
      name: params.name,
      shared: params.shared,
      data: params.data,
      type: params.type,
      entity_id: params.entityId
    }
  });

export const updateLayout = (organizationId, layoutId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/layouts/${layoutId}`,
    method: "PATCH",
    label: UPDATE_LAYOUT,
    affectedRequests: [GET_LAYOUTS, GET_LAYOUT],
    params: {
      name: params.name,
      shared: params.shared,
      data: params.data
    }
  });

export const deleteLayout = (organizationId, layoutId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/layouts/${layoutId}`,
    method: "DELETE",
    label: DELETE_LAYOUT,
    affectedRequests: [GET_LAYOUTS],
    entityId: layoutId
  });
