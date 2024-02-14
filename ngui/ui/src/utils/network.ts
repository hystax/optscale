import queryString from "query-string";
import { dispatchSearchParamsChangeEvent } from "./events";
import { filterEmpty, removeKey } from "./objects";

// TODO: make network utils reactive

// TODO: Make «parseBooleans» part of the «options»
export const getQueryParams = (parseBooleans = true, options = {}) =>
  queryString.parse(window.location.search, { parseBooleans, ...options });

export const getSearch = () => window.location.search;

export const getFullPath = () => `${window.location.pathname}${window.location.search}`;

export const getPathname = () => window.location.pathname;

export const setQueryParams = (stringURL) => {
  dispatchSearchParamsChangeEvent(queryString.parse(stringURL, { parseBooleans: true }));
  window.history.replaceState(null, null, stringURL);
};

export const getStringUrl = (objectUrl, ifEmpty = null, options = {}) => {
  const { allowEmptyString = false } = options;

  const cleanObject = filterEmpty(objectUrl, { allowEmptyString });
  if (Object.keys(cleanObject).length === 0) {
    return ifEmpty ?? getPathname();
  }
  return `?${queryString.stringify(cleanObject)}`;
};

export const updateQueryParams = (paramsObject, options = {}) => {
  const { allowEmptyString } = options;

  const queryParams = getQueryParams();
  const newQueryParams = { ...queryParams, ...paramsObject };
  setQueryParams(getStringUrl(newQueryParams, null, { allowEmptyString }));
};

export const removeQueryParam = (key) => {
  const queryParams = getQueryParams();
  const newQueryParams = removeKey(queryParams, key);
  setQueryParams(getStringUrl(newQueryParams));
};

/**
 *
 * @param {Object} params - object that describes parameters name and value
 *
 * @returns {string} string that represents query parameters
 *
 * @example
 * const params = {
 *  name: "Sally",
 *  surname: "Wong",
 *  age: 27
 * }
 * const queryString = formQueryString(params)
 * // queryString = "age=27&name=Sally&surname=Wong"
 *
 */
export const formQueryString = (params: Record<string, unknown>) => queryString.stringify(params);

export const getMenuRootUrl = (menu) => {
  const currentPath = getPathname();
  const currentQueryParams = getQueryParams();
  const menuItems = menu.reduce((result, value) => [...result, ...value.items], []);
  const activeElement = menuItems.find(
    (el) => typeof el.isActive === "function" && el.isActive(currentPath, currentQueryParams)
  );
  if (activeElement) {
    return activeElement.route.link;
  }
  return currentPath;
};
