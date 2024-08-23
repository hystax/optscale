import { SET_SELECTED_TASK_LEADERBOARD_ID, SET_OVERVIEW_BREAKDOWN } from "./actionTypes";

export const setTaskOverviewBreakdown = (taskId: string, breakdowns: string[]) => ({
  type: SET_OVERVIEW_BREAKDOWN,
  payload: { taskId, breakdowns }
});

export const setSelectedTaskLeaderboardId = (taskId: string, leaderboardId: string) => ({
  type: SET_SELECTED_TASK_LEADERBOARD_ID,
  payload: {
    taskId,
    leaderboardId
  }
});
