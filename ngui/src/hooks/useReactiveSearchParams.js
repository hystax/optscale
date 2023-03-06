import { useCallback, useEffect, useState } from "react";
import { areSearchParamsEqual } from "api/utils";
import { addSearchParamsChangeListener, removeSearchParamsChangeListener } from "utils/events";
import { getQueryParams } from "utils/network";

export const useReactiveSearchParams = (queryParamsToListen = []) => {
  const [searchParams, setSearchParams] = useState(() => {
    const allParams = getQueryParams();

    return Object.fromEntries(queryParamsToListen.map((paramName) => [paramName, allParams[paramName]]));
  });

  const listener = useCallback(
    (event) => {
      const { params } = event.detail;

      const listenedParams = Object.fromEntries(
        queryParamsToListen.map((queryParamName) => [queryParamName, params[queryParamName]])
      );

      if (!areSearchParamsEqual(listenedParams, searchParams)) {
        setSearchParams(Object.fromEntries(queryParamsToListen.map((paramName) => [paramName, params[paramName]])));
      }
    },
    [queryParamsToListen, searchParams]
  );

  useEffect(() => {
    addSearchParamsChangeListener(listener);

    return () => removeSearchParamsChangeListener(listener);
  }, [listener]);

  return searchParams;
};
