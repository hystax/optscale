import { SET_LEADERBOARD_DATASET, SET_OVERVIEW_BREAKDOWN } from "./actionTypes";

export const setTaskOverviewBreakdown = (taskId: string, breakdowns: string[]) => ({
  type: SET_OVERVIEW_BREAKDOWN,
  payload: { taskId, breakdowns }
});

export const setTaskLeaderboardDataset = (taskId: string, leaderboardDatasetId: string) => ({
  type: SET_LEADERBOARD_DATASET,
  payload: {
    taskId,
    leaderboardDatasetId
  }
});
