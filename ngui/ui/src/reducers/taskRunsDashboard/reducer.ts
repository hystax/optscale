import { SET_TASK_RUNS_DASHBOARD } from "./actionTypes";

export const TASK_RUNS_DASHBOARD = "taskRunsDashboard";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_TASK_RUNS_DASHBOARD: {
      return {
        ...state,
        [action.payload.taskId]: action.payload.dashboardId
      };
    }
    default:
      return state;
  }
};

export default reducer;
