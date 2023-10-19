import { isObject, removeUndefinedValues } from "utils/objects";
import { getHash } from "utils/strings";
import { API } from "./actionTypes";
import { ERROR_HANDLER_TYPE_ALERT, SUCCESS_HANDLER_TYPE_LOCAL } from "./constants";

export const getApiUrl = (client, version = "v2") => {
  const baseUrl = `/${client}/${version}`;
  return import.meta.env.DEV ? `/api${baseUrl}` : baseUrl;
};

export const apiAction = ({
  url = "",
  method = "POST",
  params = null,
  onSuccess = null,
  entityId = "",
  label = "",
  ttl = 0,
  hash = 0,
  errorHandlerType = ERROR_HANDLER_TYPE_ALERT,
  successHandlerType = SUCCESS_HANDLER_TYPE_LOCAL,
  successHandlerPayload,
  headersOverride = {},
  affectedRequests = [],
  allowMultipleRequests = false
}) => ({
  type: API,
  payload: {
    url,
    method,
    params,
    onSuccess,
    entityId,
    label,
    ttl,
    hash,
    errorHandlerType,
    successHandlerType,
    successHandlerPayload,
    headersOverride,
    affectedRequests,
    allowMultipleRequests
  }
});

const immutableArraySort = (arr) => [...arr].sort();
const sortValue = (value) => {
  if (Array.isArray(value)) {
    return immutableArraySort(value);
  }

  if (isObject(value)) {
    const sortedValueEntries = Object.entries(value)
      .map(([entryName, entryValue]) => [entryName, Array.isArray(entryValue) ? immutableArraySort(entryValue) : entryValue])
      .sort();

    return Object.fromEntries(sortedValueEntries);
  }

  return value ?? {};
};

/**
 * It is NOT stable JSON stringify.
 * This implementation only works for:
 *   - sortable arrays
 *   - one level depth objects
 *
 *   OK: `[], 1, "hello!", null, undefined, {b: 1, c: 2, a: [3, 4, 1]}`
 *
 *   FAIL: `{ b: 1, a: { b: 1, a: 0 } }`
 *
 */
const sortedStringify = (value) => JSON.stringify(sortValue(value));

// we using sort util to prevent different hashes for not-the-same-props-order objects or arrays
export const hashParams = (params) => getHash(sortedStringify(params));

const convertSearchParamValuesToArray = (params) =>
  Object.fromEntries(Object.entries(params).map(([paramName, paramValue]) => [paramName, [paramValue].flat()]));

export const areSearchParamsEqual = (params1, params2) =>
  hashParams(convertSearchParamValuesToArray(removeUndefinedValues(params1))) ===
  hashParams(convertSearchParamValuesToArray(removeUndefinedValues(params2)));
