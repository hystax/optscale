import { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getIntersection, isEmpty as isEmptyArray } from "utils/arrays";
import { getQueryParams, updateQueryParams } from "utils/network";
import { setBreakdowns as setBreakdownsActionCreator } from "./actionCreator";
import { MODEL_BREAKDOWN } from "./reducer";

export const useModelBreakdownState = ({
  breakdownNames,
  queryParamName,
  modelId,
  storeId,
  initialSelectedBreakdowns = [],
  fallbackBreakdowns = []
}) => {
  const dispatch = useDispatch();

  const reduxData = useSelector((state) => {
    const storeData = state[MODEL_BREAKDOWN]?.[modelId]?.[storeId] ?? undefined;

    return storeData;
  });

  const [selectedBreakdowns, setSelectedBreakdowns] = useState(() => {
    const { [queryParamName]: breakdownByQueryParameter } = getQueryParams();

    const getBreakdowns = () => {
      if (breakdownByQueryParameter) {
        const paramsArray = [breakdownByQueryParameter].flat();

        return paramsArray;
      }

      if (reduxData !== undefined && isEmptyArray(reduxData)) {
        return [];
      }

      const breakdowns = getIntersection(breakdownNames, reduxData ?? []);

      if (isEmptyArray(breakdowns)) {
        if (!isEmptyArray(initialSelectedBreakdowns)) {
          return initialSelectedBreakdowns;
        }

        if (!isEmptyArray(fallbackBreakdowns)) {
          return fallbackBreakdowns;
        }

        return [];
      }

      return breakdowns;
    };

    return getIntersection(breakdownNames, getBreakdowns());
  });

  useEffect(() => {
    dispatch(setBreakdownsActionCreator(storeId, modelId, selectedBreakdowns));
  }, [modelId, dispatch, selectedBreakdowns, storeId]);

  useEffect(() => {
    updateQueryParams({
      [queryParamName]: selectedBreakdowns
    });
  }, [queryParamName, selectedBreakdowns]);

  const addBreakdown = useCallback(
    (breakdownName) => {
      setSelectedBreakdowns([...selectedBreakdowns, breakdownName]);
    },
    [selectedBreakdowns]
  );

  const removeBreakdown = useCallback(
    (breakdownName) => {
      const breakdowns = selectedBreakdowns.filter((name) => name !== breakdownName);
      setSelectedBreakdowns(breakdowns);
    },
    [selectedBreakdowns]
  );

  return {
    selectedBreakdowns,
    addBreakdown,
    removeBreakdown
  };
};
