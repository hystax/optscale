import { SET_APPLICATION_BREAKDOWNS } from "./actionTypes";

export const setBreakdowns = (storeId, applicationId, breakdowns) => ({
  type: SET_APPLICATION_BREAKDOWNS,
  payload: { storeId, id: applicationId, breakdowns }
});
