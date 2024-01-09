import { useEffect, useState } from "react";
import { LeaderboardDatasets } from "components/MlModelLeaderboard/components";
import TableLoader from "components/TableLoader";
import MlLeaderboardsService from "services/MlLeaderboardsService";
import { isEmpty as isEmptyArray } from "utils/arrays";

const MlModelLeaderboardDatasetsContainer = ({ leaderboard }) => {
  const { useGetLeaderboardDatasets } = MlLeaderboardsService();

  const { isLoading, leaderboardDatasets } = useGetLeaderboardDatasets(leaderboard.id);

  const [selectedLeaderboardDataset, setSelectedLeaderboardDataset] = useState(null);

  useEffect(() => {
    setSelectedLeaderboardDataset((currentlySelectedDataset) => {
      if (isEmptyArray(leaderboardDatasets)) {
        return null;
      }

      const updatedCurrentlySelectedDataset = currentlySelectedDataset
        ? leaderboardDatasets.find(({ id }) => id === currentlySelectedDataset.id)
        : null;

      return updatedCurrentlySelectedDataset || leaderboardDatasets[0];
    });
  }, [leaderboardDatasets]);

  return isLoading ? (
    <TableLoader />
  ) : (
    <LeaderboardDatasets
      leaderboard={leaderboard}
      leaderboardDatasets={leaderboardDatasets}
      selectedLeaderboardDataset={selectedLeaderboardDataset}
      onSelectedLeaderboardDashboardChange={setSelectedLeaderboardDataset}
    />
  );
};

export default MlModelLeaderboardDatasetsContainer;
