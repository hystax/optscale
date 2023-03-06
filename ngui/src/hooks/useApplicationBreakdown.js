import { useCallback, useEffect } from "react";
import { useApplicationBreakdownState } from "reducers/applicationBreakdown/useApplicationBreakdownState";
import { getIntersection } from "utils/arrays";
import { getQueryParams, updateQueryParams } from "utils/network";

export const useApplicationBreakdown = ({ modelId, queryParamName, breakdownNames, storeId }) => {
  const { selectedBreakdowns, setBreakdowns, addBreakdown, removeBreakdown } = useApplicationBreakdownState({
    applicationId: modelId,
    storeId,
    defaultSelectedBreakdowns: breakdownNames.slice(0, 3)
  });

  useEffect(() => {
    const { [queryParamName]: breakdownByQueryParameter } = getQueryParams();

    if (breakdownByQueryParameter) {
      const paramsArray = [breakdownByQueryParameter].flat();

      setBreakdowns(paramsArray);
    }
  }, [queryParamName, setBreakdowns]);

  useEffect(() => {
    updateQueryParams({
      [queryParamName]: selectedBreakdowns
    });
  }, [queryParamName, selectedBreakdowns]);

  const onBreakdownChange = useCallback(
    (name, checked) => {
      if (checked) {
        addBreakdown(name);
      } else {
        removeBreakdown(name);
      }
    },
    [addBreakdown, removeBreakdown]
  );

  return {
    selectedBreakdowns: getIntersection(breakdownNames, selectedBreakdowns),
    onBreakdownChange
  };
};
