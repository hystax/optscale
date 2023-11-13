import { useState, useEffect } from "react";
import { getQueryParams, updateQueryParams } from "utils/network";

/**
 * Syncing url query param with state
 * @param {Object} props State definition object
 * @param {string} props.queryParamName Parameter name from url search string
 * @param {string[]} [props.possibleStates] Possible query values array
 * @param {string} [props.defaultValue] Default state value if query is not set or not presented in possible states
 * @param {boolean} [props.parameterIsArray] Query parameter value always parses as array, even for single value
 * @returns {[string | string[], function]} React state/setState
 */
export const useSyncQueryParamWithState = ({ queryParamName, possibleStates, defaultValue = "", parameterIsArray = false }) => {
  const [query, setQuery] = useState(() => {
    const { [queryParamName]: queryValue } = getQueryParams();

    if (!queryValue) {
      return defaultValue;
    }

    if (possibleStates) {
      return possibleStates.includes(queryValue) ? queryValue : defaultValue;
    }

    if (parameterIsArray && !Array.isArray(queryValue)) {
      return [queryValue];
    }

    return queryValue;
  });

  useEffect(() => {
    updateQueryParams({ [queryParamName]: query });
  }, [query, queryParamName]);

  return [query, setQuery];
};
