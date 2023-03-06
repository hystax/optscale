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
  CREATE_CLOUD_ACCOUNT,
  GET_POOL,
  GET_CLOUD_ACCOUNTS,
  GET_DETAILED_CLOUD_ACCOUNTS,
  GET_CLOUD_ACCOUNT_DETAILS,
  DELETE_CLOUD_ACCOUNT,
  UPDATE_CLOUD_ACCOUNT,
  SET_POOL,
  SET_CLOUD_ACCOUNT_DETAILS,
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
  GET_TECHNICAL_AUDIT,
  SET_TECHNICAL_AUDIT,
  UPDATE_TECHNICAL_AUDIT,
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
  GET_ML_APPLICATIONS,
  SET_ML_APPLICATIONS,
  GET_ML_GLOBAL_PARAMETERS,
  SET_ML_GLOBAL_PARAMETERS,
  GET_ML_GLOBAL_PARAMETER,
  SET_ML_GLOBAL_PARAMETER,
  CREATE_GLOBAL_PARAMETER,
  UPDATE_GLOBAL_PARAMETER,
  DELETE_GLOBAL_PARAMETER,
  CREATE_ML_APPLICATION,
  GET_PROFILING_TOKEN,
  SET_PROFILING_TOKEN,
  GET_ML_EXECUTORS,
  SET_ML_EXECUTORS,
  GET_ML_EXECUTORS_BREAKDOWN,
  SET_ML_EXECUTORS_BREAKDOWN,
  SET_ML_APPLICATION,
  GET_ML_APPLICATION,
  UPDATE_ML_APPLICATION,
  DELETE_ML_APPLICATION,
  SET_ML_APPLICATION_RUNS,
  GET_ML_APPLICATION_RUNS,
  SET_ML_RUN_DETAILS,
  GET_ML_RUN_DETAILS,
  SET_ML_RUN_DETAILS_BREAKDOWN,
  GET_ML_RUN_DETAILS_BREAKDOWN
} from "./actionTypes";
import {
  onUpdateOrganizationOption,
  onSuccessUpdateInvitation,
  onSuccessCreateCloudAccount,
  onSuccessDisconnectCloudAccount,
  onSuccessCreatePool,
  onSuccessDeletePool,
  onSuccessGetCurrentEmployee,
  onSuccessCreatePoolPolicy,
  onSuccessCreateResourceConstraint,
  onSuccessDeleteResourceConstraint,
  onSuccessGetOptimizations,
  onSuccessUpdateOptimizations,
  onSuccessGetCloudAccounts,
  onSuccessCreateLiveDemo,
  onSuccessUpdateAssignmentRulePriority,
  onFinOpsChecklist,
  onUpdateTechnicalAudit,
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
  onUpdateMlApplication
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

export const getOrganizationOptions = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ORGANIZATION_OPTIONS),
    hash: hashParams(organizationId),
    label: GET_ORGANIZATION_OPTIONS
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

export const getDetailedCloudAccounts = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_accounts`,
    method: "GET",
    onSuccess: onSuccessGetCloudAccounts,
    label: GET_DETAILED_CLOUD_ACCOUNTS,
    ttl: MINUTE,
    hash: hashParams(organizationId),
    params: {
      details: true
    }
  });

export const getCloudAccounts = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_accounts`,
    method: "GET",
    onSuccess: onSuccessGetCloudAccounts,
    label: GET_CLOUD_ACCOUNTS,
    hash: hashParams(organizationId),
    ttl: 2 * MINUTE,
    params: {
      details: false
    }
  });

export const getCloudAccountDetails = (cloudAccountId, details = false) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${cloudAccountId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_CLOUD_ACCOUNT_DETAILS),
    label: GET_CLOUD_ACCOUNT_DETAILS,
    ttl: MINUTE,
    hash: hashParams(cloudAccountId),
    params: {
      details
    }
  });

export const createCloudAccount = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/cloud_accounts`,
    method: "POST",
    onSuccess: onSuccessCreateCloudAccount,
    affectedRequests: [GET_AVAILABLE_FILTERS],
    label: CREATE_CLOUD_ACCOUNT,
    params
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

export const disconnectCloudAccount = (id) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${id}`,
    method: "DELETE",
    onSuccess: onSuccessDisconnectCloudAccount(id),
    affectedRequests: [GET_AVAILABLE_FILTERS],
    label: DELETE_CLOUD_ACCOUNT
  });

export const updateCloudAccount = (id, params) =>
  apiAction({
    url: `${API_URL}/cloud_accounts/${id}`,
    method: "PATCH",
    label: UPDATE_CLOUD_ACCOUNT,
    affectedRequests: [GET_CLOUD_ACCOUNT_DETAILS, GET_DATA_SOURCE_NODES],
    params
  });

export const getPool = (poolId, children = false, details = false) =>
  apiAction({
    url: `${API_URL}/pools/${poolId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_POOL),
    label: GET_POOL,
    ttl: MINUTE,
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
    onSuccess: onSuccessCreatePool,
    affectedRequests: [GET_AVAILABLE_POOLS, GET_AVAILABLE_FILTERS],
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
    ttl: MINUTE,
    hash: hashParams({ ...params, organizationId }),
    params: {
      permission: params.permission || ["INFO_ORGANIZATION"],
      condition: params.condition
    }
  });

export const getPoolOwners = (poolId, excludeMyself = false) =>
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
    label: CREATE_POOL_POLICY
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
    affectedRequests: [GET_GLOBAL_POOL_POLICIES]
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
    affectedRequests: [GET_RESOURCE, ...affectedRequests],
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

export const getOptimizations = (organizationId, params = {}) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/optimizations`,
    method: "GET",
    onSuccess: onSuccessGetOptimizations,
    label: GET_OPTIMIZATIONS,
    hash: hashParams({ organizationId, type: params.type }),
    ttl: 5 * MINUTE,
    params: {
      type: params.type,
      limit: params.limit,
      status: params.status,
      cloud_account_id: params.cloudAccountIds
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
    affectedRequests: [GET_OPTIMIZATIONS],
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

export const createLiveDemo = () =>
  apiAction({
    url: `${API_URL}/live_demo`,
    method: "POST",
    onSuccess: onSuccessCreateLiveDemo,
    label: CREATE_LIVE_DEMO,
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL
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
    affectedRequests: [GET_RESOURCE],
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

export const getTechnicalAudit = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/technical_audit_application`,
    method: "GET",
    onSuccess: handleSuccess(SET_TECHNICAL_AUDIT),
    ttl: HOUR,
    hash: hashParams(organizationId),
    label: GET_TECHNICAL_AUDIT
  });

export const updateTechnicalAudit = (organizationId, value) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/options/technical_audit_application`,
    method: "PATCH",
    label: UPDATE_TECHNICAL_AUDIT,
    onSuccess: onUpdateTechnicalAudit,
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

export const getMlApplications = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_APPLICATIONS),
    hash: hashParams(organizationId),
    label: GET_ML_APPLICATIONS
  });

export const getMlApplication = (organizationId, applicationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications/${applicationId}`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_APPLICATION),
    hash: hashParams({ organizationId, applicationId }),
    label: GET_ML_APPLICATION
  });

export const getMlApplicationRuns = (organizationId, applicationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications/${applicationId}/runs`,
    method: "GET",
    ttl: 5 * MINUTE,
    onSuccess: handleSuccess(SET_ML_APPLICATION_RUNS),
    hash: hashParams({ organizationId, applicationId }),
    label: GET_ML_APPLICATION_RUNS
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

export const createMlApplication = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications`,
    method: "POST",
    label: CREATE_ML_APPLICATION,
    params,
    affectedRequests: [GET_ML_APPLICATIONS]
  });

export const updateMlApplication = (organizationId, applicationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications/${applicationId}`,
    method: "PATCH",
    label: UPDATE_ML_APPLICATION,
    onSuccess: onUpdateMlApplication,
    params,
    affectedRequests: [GET_ML_APPLICATIONS]
  });

export const deleteMlApplication = (organizationId, applicationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/applications/${applicationId}`,
    method: "DELETE",
    label: DELETE_ML_APPLICATION,
    affectedRequests: [GET_ML_APPLICATIONS]
  });

export const getMlGlobalParameters = (organizationId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/goals`,
    method: "GET",
    label: GET_ML_GLOBAL_PARAMETERS,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId }),
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL,
    onSuccess: handleSuccess(SET_ML_GLOBAL_PARAMETERS)
  });

export const getMlGlobalParameter = (organizationId, parameterId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/goals/${parameterId}`,
    method: "GET",
    label: GET_ML_GLOBAL_PARAMETER,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, parameterId }),
    onSuccess: handleSuccess(SET_ML_GLOBAL_PARAMETER)
  });

export const createGlobalParameter = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/goals`,
    method: "POST",
    label: CREATE_GLOBAL_PARAMETER,
    params,
    affectedRequests: [GET_ML_GLOBAL_PARAMETERS]
  });

export const updateGlobalParameter = (organizationId, parameterId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/goals/${parameterId}`,
    method: "PATCH",
    label: UPDATE_GLOBAL_PARAMETER,
    affectedRequests: [GET_ML_GLOBAL_PARAMETERS],
    params
  });

export const deleteGlobalParameter = (organizationId, parameterId) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/goals/${parameterId}`,
    method: "DELETE",
    label: DELETE_GLOBAL_PARAMETER,
    affectedRequests: [GET_ML_GLOBAL_PARAMETERS]
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
      application_id: params.applicationIds,
      run_id: params.runIds
    }
  });

export const getMlExecutorsBreakdown = (organizationId, params) =>
  apiAction({
    url: `${API_URL}/organizations/${organizationId}/executors_breakdown`,
    method: "GET",
    onSuccess: handleSuccess(SET_ML_EXECUTORS_BREAKDOWN),
    label: GET_ML_EXECUTORS_BREAKDOWN,
    ttl: 5 * MINUTE,
    hash: hashParams({ organizationId, ...params }),
    // Filtering by date is not yet supported by the backend
    params: {
      breakdown_by: params.breakdownBy
      // start_date: params.startDate,
      // end_date: params.endDate,
    }
  });
