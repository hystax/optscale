import { CHANGE_PERIOD_TYPE } from "./actionTypes";

export const changePeriodType = (type) => ({
  type: CHANGE_PERIOD_TYPE,
  payload: type
});
