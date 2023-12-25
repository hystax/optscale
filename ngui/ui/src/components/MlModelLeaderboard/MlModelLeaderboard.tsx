import React from "react";
import TableLoader from "components/TableLoader";
import MlModelLeaderboardDatasetsContainer from "containers/MlModelLeaderboardDatasetsContainer";
import { SetupLeaderboardsInvitation } from "./components";

const MlModelLeaderboard = ({ leaderboard, isLoading = false }) => {
  if (isLoading) {
    return <TableLoader />;
  }

  return leaderboard?.id ? <MlModelLeaderboardDatasetsContainer leaderboard={leaderboard} /> : <SetupLeaderboardsInvitation />;
};

export default MlModelLeaderboard;
