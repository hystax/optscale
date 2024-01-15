import { SET_LEADERBOARD_DATASET, SET_MODEL_OVERVIEW_CHART } from "./actionTypes";

export const MODEL_BREAKDOWN = "modelBreakdown";

export const STORE_ACCESSORS = Object.freeze({
  MODEL_RUNS: "model_runs",
  LEADERBOARD_DATASET_ID: "leaderboard_dataset_id"
});

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_MODEL_OVERVIEW_CHART: {
      return {
        ...state,
        [action.payload.taskId]: {
          ...state[action.payload.taskId],
          [STORE_ACCESSORS.MODEL_RUNS]: action.payload.breakdowns
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
