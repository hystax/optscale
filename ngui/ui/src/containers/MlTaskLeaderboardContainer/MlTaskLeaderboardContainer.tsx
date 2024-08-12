import { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";
import { GET_ML_LEADERBOARD } from "api/restapi/actionTypes";
import MlTaskLeaderboard from "components/MlTaskLeaderboard";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  getStoreLeaderboardDatasetId,
  setStoreLeaderboardDatasetId,
  useTaskSelectedLeaderboardDatasetId
} from "reducers/taskBreakdown/useTaskSelectedLeaderboardDatasetId";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import { isEmpty as isEmptyArray } from "utils/arrays";

const MlTaskLeaderboardContainer = ({ task }) => {
  const { taskId } = useParams() as { taskId: string };
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const {
    useGetLeaderboardOnDemand,
    useGetLeaderboardDatasetsOnDemand,
    useGetLeaderboardDatasetOnDemand,
    useGetLeaderboardDatasetDetailsOnDemand
  } = MlLeaderboardsService();

  const { isLoading: isGetLeaderboardLoading, data: leaderboard, getData: getLeaderboard } = useGetLeaderboardOnDemand();
  const {
    isLoading: isGetLeaderboardDatasetsLoading,
    data: leaderboardDatasets,
    getData: getLeaderboardDatasets
  } = useGetLeaderboardDatasetsOnDemand();
  const {
    isLoading: isGetLeaderboardDatasetLoading,
    data: leaderboardDataset,
    getData: getLeaderboardDataset
  } = useGetLeaderboardDatasetOnDemand();
  const {
    isLoading: isGetLeaderboardDatasetDetailsLoading,
    data: leaderboardDatasetDetails,
    getData: getLeaderboardDatasetDetails
  } = useGetLeaderboardDatasetDetailsOnDemand();

  const getLeaderboardDatasetData = useCallback(
    (leaderboardDatasetId: string) =>
      Promise.all([getLeaderboardDataset(leaderboardDatasetId), getLeaderboardDatasetDetails(leaderboardDatasetId)]),
    [getLeaderboardDataset, getLeaderboardDatasetDetails]
  );

  const { shouldInvoke } = useApiState(GET_ML_LEADERBOARD, {
    organizationId,
    taskId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        getLeaderboard(taskId).then((leaderboardData) => {
          if (leaderboardData.id) {
            return getLeaderboardDatasets(leaderboardData.id).then((apiLeaderboardDatasets) => {
              if (!isEmptyArray(apiLeaderboardDatasets)) {
                const storedLeaderboardDatasetId = getStoreLeaderboardDatasetId(getState(), taskId);

                const leaderboardDatasetId =
                  apiLeaderboardDatasets.find(({ id }) => id === storedLeaderboardDatasetId)?.id ??
                  apiLeaderboardDatasets[0].id;

                setStoreLeaderboardDatasetId(dispatch)(taskId, leaderboardDatasetId);

                return getLeaderboardDatasetData(leaderboardDatasetId);
              }
              return Promise.resolve();
            });
          }
          return Promise.resolve();
        });
      });
    }
  }, [dispatch, getLeaderboard, getLeaderboardDatasetData, getLeaderboardDatasets, shouldInvoke, taskId]);

  const { selectedLeaderboardDatasetId, onSelectionChange } = useTaskSelectedLeaderboardDatasetId(taskId as string);

  return (
    <MlTaskLeaderboard
      task={task}
      leaderboard={leaderboard}
      leaderboardDatasets={leaderboardDatasets}
      leaderboardDataset={leaderboardDataset}
      selectedLeaderboardDatasetId={selectedLeaderboardDatasetId}
      leaderboardDatasetDetails={leaderboardDatasetDetails}
      onSelectedLeaderboardDatasetIdChange={(leaderboardDatasetId: string) => {
        onSelectionChange(leaderboardDatasetId);
        getLeaderboardDatasetData(leaderboardDatasetId);
      }}
      onCreateLeaderboardDataset={(newLeaderboardDataset) => {
        getLeaderboardDatasets(leaderboard.id).then(() => {
          onSelectionChange(newLeaderboardDataset.id);
          getLeaderboardDatasetData(newLeaderboardDataset.id);
        });
      }}
      onUpdateLeaderboardDataset={(updatedLeaderboardDataset) => {
        console.log("updatedLeaderboardDataset", updatedLeaderboardDataset);
        getLeaderboardDatasets(leaderboard.id).then(() => {
          onSelectionChange(updatedLeaderboardDataset.id);
          getLeaderboardDatasetData(updatedLeaderboardDataset.id);
        });
      }}
      isLoadingProps={{
        isGetLeaderboardLoading,
        isGetLeaderboardDatasetsLoading,
        isGetLeaderboardDatasetLoading,
        isGetLeaderboardDatasetDetailsLoading
      }}
    />
  );
};

export default MlTaskLeaderboardContainer;
