import { SET_TASK_RUNS_DASHBOARD } from "./actionTypes";

export const setTaskRunsDashboardId = ({ taskId, dashboardId }) => ({
  type: SET_TASK_RUNS_DASHBOARD,
  payload: { taskId, dashboardId }
});
