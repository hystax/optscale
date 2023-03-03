import { useState, useEffect } from "react";
import { getQueryParams, updateQueryParams } from "utils/network";

/**
 * Syncing url query param with state
 * @param {Object} props State definition object
 * @param {string} props.queryParamName Parameter name from url search string
 * @param {string[]} [props.possibleStates] Possible query values array
 * @param {string} [props.defaultValue] Default state value if query is not set or not presented in possible states
 * @returns {[string | string[], function]} React state/setState
 */
export const useSyncQueryParamWithState = ({ queryParamName, possibleStates, defaultValue = "" }) => {
  const [query, setQuery] = useState(() => {
    const { [queryParamName]: queryValue } = getQueryParams();

    if (possibleStates) {
      return possibleStates.includes(queryValue) ? queryValue : defaultValue;
    }

    return queryValue ?? defaultValue;
  });

  useEffect(() => {
    updateQueryParams({ [queryParamName]: query });
  }, [query, queryParamName]);

  return [query, setQuery];
};
