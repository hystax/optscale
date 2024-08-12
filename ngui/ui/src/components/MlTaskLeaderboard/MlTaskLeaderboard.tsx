import TableLoader from "components/TableLoader";
import { LeaderboardDatasets, SetupLeaderboardsInvitation } from "./components";

const MlTaskLeaderboard = ({
  task,
  leaderboard,
  leaderboardDatasets,
  leaderboardDataset,
  selectedLeaderboardDatasetId,
  leaderboardDatasetDetails,
  onSelectedLeaderboardDatasetIdChange,
  onCreateLeaderboardDataset,
  onUpdateLeaderboardDataset,
  isLoadingProps = {}
}) => {
  if (isLoadingProps.isGetLeaderboardLoading || isLoadingProps.isGetLeaderboardDatasetsLoading) {
    return <TableLoader />;
  }

  if (leaderboard?.id) {
    return (
      <LeaderboardDatasets
        task={task}
        leaderboard={leaderboard}
        leaderboardDatasets={leaderboardDatasets}
        leaderboardDataset={leaderboardDataset}
        selectedLeaderboardDatasetId={selectedLeaderboardDatasetId}
        leaderboardDatasetDetails={leaderboardDatasetDetails}
        onSelectedLeaderboardDatasetIdChange={onSelectedLeaderboardDatasetIdChange}
        onCreateLeaderboardDataset={onCreateLeaderboardDataset}
        onUpdateLeaderboardDataset={onUpdateLeaderboardDataset}
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
