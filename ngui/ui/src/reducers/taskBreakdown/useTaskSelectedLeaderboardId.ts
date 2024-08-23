import { useDispatch, useSelector } from "react-redux";
import { setSelectedTaskLeaderboardId } from "./actionCreator";
import { TASK_BREAKDOWN, STORE_ACCESSORS } from "./reducer";

export const getStoreLeaderboardId = (state, taskId) =>
  state[TASK_BREAKDOWN]?.[taskId]?.[STORE_ACCESSORS.LEADERBOARD_ID] ?? undefined;

export const setStoreLeaderboardId = (dispatch) => (taskId, leaderboardId) => {
  dispatch(setSelectedTaskLeaderboardId(taskId, leaderboardId));
};

export const useTaskSelectedLeaderboardId = (taskId: string) => {
  const dispatch = useDispatch();

  const selectedLeaderboardId = useSelector((state) => {
    const storeData = getStoreLeaderboardId(state, taskId);

    return storeData;
  });

  const onSelectionChange = (newSelectedLeaderboardId: string) => {
    setStoreLeaderboardId(dispatch)(taskId, newSelectedLeaderboardId);
  };

  return {
    selectedLeaderboardId,
    onSelectionChange
  };
};
