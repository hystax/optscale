import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { CHANGE_PERIOD_TYPE } from "./actionTypes";

export const EXPENSES_BREAKDOWN_PERIOD_TYPE = "expensesBreakdownPeriodType";

const reducer = (state = EXPENSES_SPLIT_PERIODS.DAILY, action) => {
  switch (action.type) {
    case CHANGE_PERIOD_TYPE:
      return action.payload;
    default:
      return state;
  }
};

export default reducer;
