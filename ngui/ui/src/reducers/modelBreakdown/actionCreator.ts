import { SET_MODEL_OVERVIEW_CHART } from "./actionTypes";

export const setModelOverviewChart = (storeId, taskId, breakdowns) => ({
  type: SET_MODEL_OVERVIEW_CHART,
  payload: { storeId, id: taskId, breakdowns }
});
