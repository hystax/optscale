import { handleSuccess } from "api/actionCreators";
import { MINUTE } from "api/constants";
import { apiAction, getApiUrl, hashParams } from "api/utils";
import {
  CREATE_USER,
  GET_ORGANIZATION_ALLOWED_ACTIONS,
  GET_TOKEN,
  GET_USER,
  SET_USER,
  RESET_PASSWORD,
  GET_POOL_ALLOWED_ACTIONS,
  GET_RESOURCE_ALLOWED_ACTIONS,
  SET_ALLOWED_ACTIONS,
  SIGN_IN,
  UPDATE_USER
} from "./actionTypes";

import { onSuccessSignIn, onSuccessCreateUser, onSuccessGetToken } from "./handlers";

export const API_URL = getApiUrl("auth");

export const getToken = ({ email, password, code }) =>
  apiAction({
    url: `${API_URL}/tokens`,
    onSuccess: onSuccessGetToken({
      isTemporary: !!code
    }),
    label: GET_TOKEN,
    params: { email, password, verification_code: code }
  });

export const signIn = (provider, params) =>
  apiAction({
    url: `${API_URL}/signin`,
    onSuccess: onSuccessSignIn,
    label: SIGN_IN,
    params: { provider, ...params }
  });

export const createUser = (name, email, password) =>
  apiAction({
    url: `${API_URL}/users`,
    onSuccess: onSuccessCreateUser,
    label: CREATE_USER,
    params: { display_name: name, email, password }
  });

export const updateUser = (userId, params = {}) =>
  apiAction({
    url: `${API_URL}/users/${userId}`,
    method: "PATCH",
    label: UPDATE_USER,
    params: { display_name: params.name, password: params.password }
  });

export const getUser = (userId) =>
  apiAction({
    url: `${API_URL}/users/${userId}`,
    method: "GET",
    onSuccess: handleSuccess(SET_USER),
    label: GET_USER,
    ttl: 30 * MINUTE
  });

export const getOrganizationAllowedActions = (params) =>
  apiAction({
    url: `${API_URL}/allowed_actions`,
    method: "GET",
    onSuccess: handleSuccess(SET_ALLOWED_ACTIONS),
    label: GET_ORGANIZATION_ALLOWED_ACTIONS,
    hash: hashParams(params),
    params: { organization: params },
    ttl: 30 * MINUTE
  });

export const getResourceAllowedActions = (params) =>
  apiAction({
    url: `${API_URL}/allowed_actions`,
    method: "GET",
    onSuccess: handleSuccess(SET_ALLOWED_ACTIONS),
    label: GET_RESOURCE_ALLOWED_ACTIONS,
    hash: hashParams(params),
    params: { cloud_resource: params },
    ttl: 30 * MINUTE
  });

export const getPoolAllowedActions = (params) =>
  apiAction({
    url: `${API_URL}/allowed_actions`,
    method: "GET",
    onSuccess: handleSuccess(SET_ALLOWED_ACTIONS),
    label: GET_POOL_ALLOWED_ACTIONS,
    hash: hashParams(params),
    params: { pool: params },
    ttl: 30 * MINUTE
  });

export const resetPassword = (email) =>
  apiAction({
    url: `${API_URL}/restore_password`,
    method: "POST",
    label: RESET_PASSWORD,
    params: { email }
  });
