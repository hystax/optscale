import Protector from "components/Protector";
import MlCreateRunArtifactContainer from "containers/MlCreateRunArtifactContainer";

const MlEditRunArtifact = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlCreateRunArtifactContainer />
  </Protector>
);

export default MlEditRunArtifact;
