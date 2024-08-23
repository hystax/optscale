import Protector from "components/Protector";
import SetupLeaderboardTemplateContainer from "containers/SetupLeaderboardTemplateContainer";

const SetupLeaderboardTemplate = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <SetupLeaderboardTemplateContainer />
  </Protector>
);

export default SetupLeaderboardTemplate;
