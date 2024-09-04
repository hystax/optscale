import axios from "axios";
import queryString from "query-string";
import { v4 as uuidv4 } from "uuid";
import { apiEnd, apiError, apiStart, apiSuccess, resetTtl } from "api";
import { API } from "api/actionTypes";
import { GET_TOKEN } from "api/auth/actionTypes";
import { signOut } from "utils/api";
import { ALERT_SEVERITY } from "utils/constants";
import { getEnvironmentVariable } from "utils/env";
import requestManager from "utils/requestManager";
import { getSuccessAlertSettingsByLabel } from "utils/successCodes";

axios.interceptors.request.use(
  (config) => {
    requestManager.addAffectedRequest(config.label, config.affectedRequests);
    return config;
  },
  (error) => Promise.reject(error)
);

const apiMiddleware =
  ({ dispatch, getState }) =>
  (next) =>
  (action) => {
    if (typeof action === "function") {
      return action(dispatch, getState);
    }

    next(action);

    if (action.type !== API) return undefined;

    const {
      url,
      method,
      params,
      onSuccess,
      label,
      ttl,
      hash,
      entityId,
      errorHandlerType,
      successHandlerType,
      successHandlerPayload,
      headersOverride: headers,
      affectedRequests,
      allowMultipleRequests
    } = action.payload;

    if (!label) return undefined;

    const state = getState();

    const { token, temporaryToken, userEmail } = state?.auth?.[GET_TOKEN] ?? {};
    const accessToken = temporaryToken || token;

    const dataOrParams = ["GET", "DELETE"].includes(method) ? "params" : "data";

    axios.defaults.baseURL = getEnvironmentVariable("VITE_BASE_URL") || "";
    axios.defaults.headers.common["Content-Type"] = "application/json";
    axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`;

    const requestId = uuidv4();

    if (!allowMultipleRequests && requestManager.hasPendingRequest(label)) {
      requestManager.cancelPreviousPendingRequests(label);
    }

    dispatch(apiStart(label, hash, entityId));

    const requestSignal = requestManager.addPendingRequest(requestId, label);

    return axios
      .request({
        url,
        method,
        headers,
        label,
        [dataOrParams]: params,
        signal: requestSignal,
        affectedRequests,
        // ?foo[]=bar1&foo[]=bar2 -> ?foo=bar1&foo=bar2
        paramsSerializer: {
          serialize: queryString.stringify
        }
      })
      .then((response) => {
        if (typeof onSuccess === "function") {
          dispatch(onSuccess(response.data, label));
        }
        const { code: successCode, getMessageParams, getSeverity } = getSuccessAlertSettingsByLabel(label);

        // resetting affected requests
        requestManager.getAffectedRequests(label).forEach((apiLabel) => dispatch(resetTtl(apiLabel)));

        dispatch(
          apiSuccess({
            label,
            response,
            ttl,
            successHandlerType,
            messageParams:
              typeof getMessageParams === "function" ? getMessageParams(params, response, successHandlerPayload) : [],
            alertSeverity:
              typeof getSeverity === "function" ? getSeverity(params, response, successHandlerPayload) : ALERT_SEVERITY.SUCCESS,
            code: successCode
          })
        );
      })
      .catch((error) => {
        let errorResponse;
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorResponse = error.response;
          // Specific error codes handling
          // TODO - investigate error codes handling instead of using Protector/Error page wrappers everywhere
          if (error.response.status === 401) {
            signOut(dispatch, {
              userEmail
            });
          }
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          errorResponse = { config: { url: error.request, params: {} } };
        } else {
          // Something happened in setting up the request that triggered an error
          errorResponse = { config: { url: error.message, params: {} } };
        }
        console.log("error: ", error, { url });
        dispatch(apiError(label, errorResponse, errorHandlerType));
      })
      .finally(() => {
        requestManager.removePendingRequest(requestId);
        if (!requestManager.hasPendingRequest(label)) {
          dispatch(apiEnd(label));
        }
      });
  };

export default apiMiddleware;
