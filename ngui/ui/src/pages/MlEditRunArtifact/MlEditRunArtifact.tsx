import Protector from "components/Protector";
import MlEditRunArtifactContainer from "containers/MlEditRunArtifactContainer";

const MlEditRunArtifact = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlEditRunArtifactContainer />
  </Protector>
);

export default MlEditRunArtifact;
