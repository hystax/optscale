import TableLoader from "components/TableLoader";
import { LeaderboardDatasets, SetupLeaderboardsInvitation } from "./components";

const MlTaskLeaderboard = ({
  leaderboard,
  leaderboardDatasets,
  leaderboardDataset,
  selectedLeaderboardDatasetId,
  leaderboardDatasetDetails,
  onSelectedLeaderboardDatasetIdChange,
  isLoadingProps = {}
}) => {
  if (isLoadingProps.isGetLeaderboardLoading || isLoadingProps.isGetLeaderboardDatasetsLoading) {
    return <TableLoader />;
  }

  if (leaderboard?.id) {
    return (
      <LeaderboardDatasets
        leaderboard={leaderboard}
        leaderboardDatasets={leaderboardDatasets}
        leaderboardDataset={leaderboardDataset}
        selectedLeaderboardDatasetId={selectedLeaderboardDatasetId}
        leaderboardDatasetDetails={leaderboardDatasetDetails}
        onSelectedLeaderboardDatasetIdChange={onSelectedLeaderboardDatasetIdChange}
        isLoadingProps={{
          isGetLeaderboardDatasetLoading: isLoadingProps.isGetLeaderboardDatasetLoading,
          isGetLeaderboardDatasetDetailsLoading: isLoadingProps.isGetLeaderboardDatasetDetailsLoading
        }}
      />
    );
  }

  return <SetupLeaderboardsInvitation />;
};

export default MlTaskLeaderboard;
