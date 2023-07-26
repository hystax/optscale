import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { getQueryParams, updateQueryParams } from "utils/network";
import { useRootData } from "./useRootData";

export const useShowDailyBreakdown = ({ reduxKey, queryParamName, actionCreator }) => {
  const dispatch = useDispatch();

  const { [queryParamName]: queryParam } = getQueryParams();

  const { rootData: showDailyBreakdownState } = useRootData(reduxKey);

  const [showDailyBreakdown, setShowExpensesDailyBreakdown] = useState(() =>
    [false, true].includes(queryParam) ? queryParam : showDailyBreakdownState
  );

  const onShowDailyBreakdownChange = (show) => {
    setShowExpensesDailyBreakdown(show);
  };

  useEffect(() => {
    updateQueryParams({
      [queryParamName]: showDailyBreakdown
    });
    dispatch(actionCreator(showDailyBreakdown));
  }, [actionCreator, dispatch, queryParamName, showDailyBreakdown]);

  return [showDailyBreakdown, onShowDailyBreakdownChange];
};
