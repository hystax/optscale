import LeaderboardDatasetDetails from "components/LeaderboardDatasetDetails";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const LeaderboardDatasetDetailsContainer = ({ leaderboard, leaderboardDatasetId }) => {
  const { useGetLeaderboardDataset, useGetLeaderboardDatasetDetails } = MlLeaderboardsService();

  const { isLoading: isGetLeaderboardDatasetLoading, leaderboardDataset } = useGetLeaderboardDataset(leaderboardDatasetId);
  const { isLoading: isGetLeaderboardDatasetDetailsLoading, leaderboardDatasetDetails } =
    useGetLeaderboardDatasetDetails(leaderboardDatasetId);

  return (
    <LeaderboardDatasetDetails
      leaderboard={leaderboard}
      leaderboardDataset={leaderboardDataset}
      leaderboardDatasetDetails={leaderboardDatasetDetails}
      isLoadingProps={{
        isGetLeaderboardDatasetLoading,
        isGetLeaderboardDatasetDetailsLoading
      }}
    />
  );
};

export default LeaderboardDatasetDetailsContainer;
