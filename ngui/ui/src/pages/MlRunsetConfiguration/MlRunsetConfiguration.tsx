import Protector from "components/Protector";
import MlRunsetConfigurationContainer from "containers/MlRunsetConfigurationContainer";

const MlRunsetConfiguration = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlRunsetConfigurationContainer />
  </Protector>
);

export default MlRunsetConfiguration;
