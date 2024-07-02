import Protector from "components/Protector";
import MlEditArtifactContainer from "containers/MlEditArtifactContainer";

const MlEditArtifact = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlEditArtifactContainer />
  </Protector>
);

export default MlEditArtifact;
