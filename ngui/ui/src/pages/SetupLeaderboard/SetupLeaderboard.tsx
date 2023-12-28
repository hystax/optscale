import Protector from "components/Protector";
import SetupLeaderboardContainer from "containers/SetupLeaderboardContainer";

const SetupLeaderboard = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <SetupLeaderboardContainer />
  </Protector>
);

export default SetupLeaderboard;
