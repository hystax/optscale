import React from "react";
import { useParams } from "react-router-dom";
import MlModelLeaderboard from "components/MlModelLeaderboard";
import MlLeaderboardsService from "services/MlLeaderboardsService";

const MlModelLeaderboardContainer = () => {
  const { taskId } = useParams();

  const { useGetLeaderboard } = MlLeaderboardsService();

  const { isLoading, leaderboard } = useGetLeaderboard(taskId);

  return <MlModelLeaderboard leaderboard={leaderboard} isLoading={isLoading} />;
};

export default MlModelLeaderboardContainer;
