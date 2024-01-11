import { SET_LEADERBOARD_DATASET, SET_MODEL_OVERVIEW_CHART } from "./actionTypes";

export const setModelOverviewChart = (taskId: string, breakdowns: string[]) => ({
  type: SET_MODEL_OVERVIEW_CHART,
  payload: { id: taskId, breakdowns }
});

export const setModelLeaderboardDataset = (taskId: string, leaderboardDatasetId: string) => ({
  type: SET_LEADERBOARD_DATASET,
  payload: {
    taskId,
    leaderboardDatasetId
  }
});
