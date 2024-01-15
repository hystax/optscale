import { useDispatch, useSelector } from "react-redux";
import { setModelLeaderboardDataset } from "./actionCreator";
import { MODEL_BREAKDOWN, STORE_ACCESSORS } from "./reducer";

export const useModelSelectedLeaderboardDatasetId = (taskId: string) => {
  const dispatch = useDispatch();

  const selectedLeaderboardDatasetId = useSelector((state) => {
    const storeData = state[MODEL_BREAKDOWN]?.[taskId]?.[STORE_ACCESSORS.LEADERBOARD_DATASET_ID] ?? undefined;

    return storeData;
  });

  const onSelectionChange = (newSelectedLeaderboardDatasetId: string) => {
    dispatch(setModelLeaderboardDataset(taskId, newSelectedLeaderboardDatasetId));
  };

  return {
    selectedLeaderboardDatasetId,
    onSelectionChange
  };
};
