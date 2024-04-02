import { useDispatch, useSelector } from "react-redux";
import { setTaskLeaderboardDataset } from "./actionCreator";
import { TASK_BREAKDOWN, STORE_ACCESSORS } from "./reducer";

export const getStoreLeaderboardDatasetId = (state, taskId) =>
  state[TASK_BREAKDOWN]?.[taskId]?.[STORE_ACCESSORS.LEADERBOARD_DATASET_ID] ?? undefined;

export const setStoreLeaderboardDatasetId = (dispatch) => (taskId, leaderboardDatasetId) => {
  dispatch(setTaskLeaderboardDataset(taskId, leaderboardDatasetId));
};

export const useTaskSelectedLeaderboardDatasetId = (taskId: string) => {
  const dispatch = useDispatch();

  const selectedLeaderboardDatasetId = useSelector((state) => {
    const storeData = getStoreLeaderboardDatasetId(state, taskId);

    return storeData;
  });

  const onSelectionChange = (newSelectedLeaderboardDatasetId: string) => {
    setStoreLeaderboardDatasetId(dispatch)(taskId, newSelectedLeaderboardDatasetId);
  };

  return {
    selectedLeaderboardDatasetId,
    onSelectionChange
  };
};
