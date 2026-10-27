import queryString from "query-string";
import { dispatchSearchParamsChangeEvent } from "./events";
import { isEmptyObject, removeKey } from "./objects";

type SearchParams = Record<
  string,
  string | number | boolean | null | undefined | Array<string | number | boolean | null | undefined>
>;

const parseSearchParams = (query: string, options = {}): SearchParams =>
  queryString.parse(query, { parseBooleans: true, parseNumbers: true, ...options });

export const stringifySearchParams = (params: SearchParams) =>
  queryString.stringify(params, {
    skipEmptyString: true,
    skipNull: true,
    strict: false,
    sort: false,
  });

export const getSearchParams = (options = {}) =>
  parseSearchParams(window.location.search, { parseBooleans: true, parseNumbers: true, ...options });

export const getSearch = () => window.location.search;

export const getFullPath = () => `${window.location.pathname}${window.location.search}`;

export const getPathname = () => window.location.pathname;

const setSearchParams = (searchParams: string) => {
  const parsedParams = parseSearchParams(searchParams);
  dispatchSearchParamsChangeEvent(parsedParams);
  window.history.replaceState(null, null, `?${searchParams}`);
};

export const updateSearchParams = (params: SearchParams) => {
  const currentSearchParams = getSearchParams();
  const newSearchParams = { ...currentSearchParams, ...params };

  setSearchParams(stringifySearchParams(newSearchParams));
};

export const removeSearchParam = (key: string) => {
  const currentSearchParams = getSearchParams();
  const newSearchParams = removeKey(currentSearchParams, key);
  setSearchParams(stringifySearchParams(newSearchParams));
};

export const buildFullPath = (path: string, params?: SearchParams) => {
  const searchParams = params && !isEmptyObject(params) ? stringifySearchParams(params) : "";
  return searchParams ? `${path}?${searchParams}` : path;
};
