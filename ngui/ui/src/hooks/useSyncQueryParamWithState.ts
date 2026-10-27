import { useState, useEffect } from "react";
import { getSearchParams, updateSearchParams } from "utils/network";

type SyncQueryParamWithStateProps<T, P extends boolean = false> = {
  queryParamName: string;
  possibleStates?: T[];
  defaultValue: P extends true ? T[] : T;
  parameterIsArray?: P;
  searchParamsGetterOptions?: {
    parseBooleans?: boolean;
    parseNumbers?: boolean;
  };
};

type ReturnType<T, P extends boolean = false> = [P extends true ? T[] : T, (value: P extends true ? T[] : T) => void];

/**
 * Syncing url query param with state
 */
export const useSyncQueryParamWithState = <T, P extends boolean = false>({
  queryParamName,
  possibleStates,
  defaultValue,
  parameterIsArray = false as P,
  searchParamsGetterOptions,
}: SyncQueryParamWithStateProps<T, P>): ReturnType<T, P> => {
  const [query, setQuery] = useState(() => {
    const params = getSearchParams(searchParamsGetterOptions);
    const queryValue = params[queryParamName] as T;

    if (queryValue === undefined) {
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
    updateSearchParams({ [queryParamName]: query });
  }, [query, queryParamName]);

  return [query, setQuery] as ReturnType<T, P>;
};
