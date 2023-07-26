import { ACCESS_DENIED, API_END, API_ERROR, API_START, API_SUCCESS, RESET_TTL } from "./actionTypes";

export const apiStart = (label, hash, entityId) => ({
  type: API_START,
  payload: { label, hash, entityId }
});

export const apiEnd = (label) => ({
  type: API_END,
  payload: label
});

export const accessDenied = (url) => ({
  type: ACCESS_DENIED,
  payload: url
});

export const apiError = (label, response, errorHandlerType) => ({
  type: API_ERROR,
  payload: {
    label,
    response,
    errorHandlerType
  }
});

export const apiSuccess = (payload) => ({
  type: API_SUCCESS,
  payload
});

export const handleSuccess = (type) => (data, label) => ({
  type,
  label,
  payload: data
});

export const resetTtl = (label) => ({
  type: RESET_TTL,
  label
});
