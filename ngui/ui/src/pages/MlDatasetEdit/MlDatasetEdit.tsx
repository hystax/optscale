import Protector from "components/Protector";
import MlDatasetEditContainer from "containers/MlDatasetEditContainer";

const MlDatasetEdit = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlDatasetEditContainer />
  </Protector>
);

export default MlDatasetEdit;
