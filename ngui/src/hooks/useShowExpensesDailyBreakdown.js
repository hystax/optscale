import { useShowDailyBreakdown } from "./useShowDailyBreakdown";

export const SHOW_EXPENSES_DAILY_BREAKDOWN = "showExpensesDailyBreakdown";

const SET_SHOW_EXPENSES_DAILY_BREAKDOWN = "SET_SHOW_EXPENSES_DAILY_BREAKDOWN";

export const reducer = (state = true, action) => {
  switch (action.type) {
    case SET_SHOW_EXPENSES_DAILY_BREAKDOWN:
      return action.payload;
    default:
      return state;
  }
};

const actionCreator = (show) => ({
  type: SET_SHOW_EXPENSES_DAILY_BREAKDOWN,
  payload: show
});

export const useShowExpensesDailyBreakdown = () =>
  useShowDailyBreakdown({
    reduxKey: SHOW_EXPENSES_DAILY_BREAKDOWN,
    queryParamName: "showExpensesDailyBreakdown",
    actionCreator
  });
