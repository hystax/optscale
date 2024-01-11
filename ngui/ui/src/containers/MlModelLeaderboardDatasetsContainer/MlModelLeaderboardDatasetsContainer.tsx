import { useParams } from "react-router-dom";
import { LeaderboardDatasets } from "components/MlModelLeaderboard/components";
import TableLoader from "components/TableLoader";
import { useModelSelectedLeaderboardDatasetId } from "reducers/modelBreakdown/useModelSelectedLeaderboardDatasetId";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import { isEmpty as isEmptyArray } from "utils/arrays";

const MlModelLeaderboardDatasetsContainer = ({ leaderboard }) => {
  const { taskId } = useParams();

  const { useGetLeaderboardDatasets } = MlLeaderboardsService();

  const { isLoading, leaderboardDatasets } = useGetLeaderboardDatasets(leaderboard.id);

  const { selectedLeaderboardDatasetId, onSelectionChange } = useModelSelectedLeaderboardDatasetId(taskId as string);

  const getSelectedLeaderboardDataset = () => {
    if (isEmptyArray(leaderboardDatasets)) {
      return null;
    }

    const selectedLeaderboardDataset = leaderboardDatasets.find(({ id }) => id === selectedLeaderboardDatasetId);

    if (selectedLeaderboardDataset) {
      return selectedLeaderboardDataset;
    }

    return leaderboardDatasets[0];
  };

  return isLoading ? (
    <TableLoader />
  ) : (
    <LeaderboardDatasets
      leaderboard={leaderboard}
      leaderboardDatasets={leaderboardDatasets}
      selectedLeaderboardDataset={getSelectedLeaderboardDataset()}
      onSelectedLeaderboardDatasetIdChange={(newLeaderboardDatasetId) => {
        onSelectionChange(newLeaderboardDatasetId);
      }}
    />
  );
};

export default MlModelLeaderboardDatasetsContainer;
