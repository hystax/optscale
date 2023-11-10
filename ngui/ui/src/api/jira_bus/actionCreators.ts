import { handleSuccess } from "api/actionCreators";
import { MINUTE, ERROR_HANDLER_TYPE_LOCAL } from "api/constants";
import { apiAction, getApiUrl, hashParams } from "api/utils";
import { UPDATE_USER_ASSIGNMENT, GET_JIRA_ORGANIZATION_STATUS, SET_JIRA_ORGANIZATION_STATUS } from "./actionTypes";

const API_URL = getApiUrl("jira_bus");

export const updateUserAssignment = (secret) =>
  apiAction({
    url: `${API_URL}/user_assignment`,
    method: "PATCH",
    label: UPDATE_USER_ASSIGNMENT,
    params: {
      secret
    },
    // TODO EK: handle error
    errorHandlerType: ERROR_HANDLER_TYPE_LOCAL
  });

export const getJiraOrganizationStatus = (organizationId) =>
  apiAction({
    url: `${API_URL}/organization/${organizationId}/status`,
    method: "GET",
    onSuccess: handleSuccess(SET_JIRA_ORGANIZATION_STATUS),
    ttl: 10 * MINUTE,
    label: GET_JIRA_ORGANIZATION_STATUS,
    hash: hashParams(organizationId)
  });
