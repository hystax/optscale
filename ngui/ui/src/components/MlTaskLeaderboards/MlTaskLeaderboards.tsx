import TableLoader from "components/TableLoader";
import { Leaderboards, SetupLeaderboardTemplateInvitation } from "./components";

const MlTaskLeaderboards = ({
  task,
  leaderboardTemplate,
  leaderboards,
  leaderboard,
  leaderboardCandidates,
  selectedLeaderboardId,
  onSelectedLeaderboardIdChange,
  onCreateLeaderboard,
  onUpdateLeaderboard,
  isLoadingProps = {}
}) => {
  if (isLoadingProps.isGetLeaderboardTemplateLoading || isLoadingProps.isGetLeaderboardsLoading) {
    return <TableLoader />;
  }

  if (leaderboardTemplate?.id) {
    return (
      <Leaderboards
        task={task}
        leaderboardTemplate={leaderboardTemplate}
        leaderboards={leaderboards}
        leaderboard={leaderboard}
        leaderboardCandidates={leaderboardCandidates}
        selectedLeaderboardId={selectedLeaderboardId}
        onSelectedLeaderboardIdChange={onSelectedLeaderboardIdChange}
        onCreateLeaderboard={onCreateLeaderboard}
        onUpdateLeaderboard={onUpdateLeaderboard}
        isLoadingProps={{
          isGetLeaderboardLoading: isLoadingProps.isGetLeaderboardLoading,
          isGetLeaderboardCandidatesLoading: isLoadingProps.isGetLeaderboardCandidatesLoading
        }}
      />
    );
  }

  return <SetupLeaderboardTemplateInvitation />;
};

export default MlTaskLeaderboards;
