import { SET_SELECTED_TASK_LEADERBOARD_ID, SET_OVERVIEW_BREAKDOWN } from "./actionTypes";

export const TASK_BREAKDOWN = "taskBreakdown";

export const STORE_ACCESSORS = Object.freeze({
  RUNS: "runs_breakdown",
  LEADERBOARD_ID: "leaderboard_id"
});

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_OVERVIEW_BREAKDOWN: {
      return {
        ...state,
        [action.payload.taskId]: {
          ...state[action.payload.taskId],
          [STORE_ACCESSORS.RUNS]: action.payload.breakdowns
        }
      };
    }
    case SET_SELECTED_TASK_LEADERBOARD_ID: {
      return {
        ...state,
        [action.payload.taskId]: {
          ...state[action.payload.taskId],
          [STORE_ACCESSORS.LEADERBOARD_ID]: action.payload.leaderboardId
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
