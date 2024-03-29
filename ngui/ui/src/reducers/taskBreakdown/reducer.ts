import { SET_LEADERBOARD_DATASET, SET_OVERVIEW_BREAKDOWN } from "./actionTypes";

export const TASK_BREAKDOWN = "taskBreakdown";

export const STORE_ACCESSORS = Object.freeze({
  RUNS: "runs_breakdown",
  LEADERBOARD_DATASET_ID: "leaderboard_dataset_id"
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
    case SET_LEADERBOARD_DATASET: {
      return {
        ...state,
        [action.payload.taskId]: {
          ...state[action.payload.taskId],
          [STORE_ACCESSORS.LEADERBOARD_DATASET_ID]: action.payload.leaderboardDatasetId
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
