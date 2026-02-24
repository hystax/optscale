import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { getSearchParams, updateSearchParams } from "utils/network";
import { useRootData } from "./useRootData";

export const useShowDailyBreakdown = ({ reduxKey, queryParamName, actionCreator }) => {
  const dispatch = useDispatch();

  const { [queryParamName]: queryParam } = getSearchParams();

  const { rootData: showDailyBreakdownState } = useRootData(reduxKey);

  const [showDailyBreakdown, setShowExpensesDailyBreakdown] = useState(() =>
    [false, true].includes(queryParam) ? queryParam : showDailyBreakdownState
  );

  const onShowDailyBreakdownChange = (show) => {
    setShowExpensesDailyBreakdown(show);
  };

  useEffect(() => {
    updateSearchParams({
      [queryParamName]: showDailyBreakdown,
    });
    dispatch(actionCreator(showDailyBreakdown));
  }, [actionCreator, dispatch, queryParamName, showDailyBreakdown]);

  return [showDailyBreakdown, onShowDailyBreakdownChange];
};
