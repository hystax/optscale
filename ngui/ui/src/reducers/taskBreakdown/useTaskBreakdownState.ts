import { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getIntersection, isEmpty as isEmptyArray } from "utils/arrays";
import { getQueryParams, updateQueryParams } from "utils/network";
import { setTaskOverviewBreakdown } from "./actionCreator";
import { TASK_BREAKDOWN, STORE_ACCESSORS } from "./reducer";

export const useTaskBreakdownState = ({
  breakdownNames,
  queryParamName,
  taskId,
  initialSelectedBreakdowns = [],
  fallbackBreakdowns = []
}) => {
  const dispatch = useDispatch();

  const reduxData = useSelector((state) => {
    const storeData = state[TASK_BREAKDOWN]?.[taskId]?.[STORE_ACCESSORS.RUNS] ?? undefined;

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
    dispatch(setTaskOverviewBreakdown(taskId, selectedBreakdowns));
  }, [taskId, dispatch, selectedBreakdowns]);

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

  const onSelectionChange = (updatedBreakdownsSelectionNames) => {
    setSelectedBreakdowns(updatedBreakdownsSelectionNames);
  };

  return {
    selectedBreakdowns,
    addBreakdown,
    removeBreakdown,
    onSelectionChange
  };
};
