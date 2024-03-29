import MlTaskCreateComponent from "components/MlTaskCreate";
import Protector from "components/Protector";

const MlTaskCreate = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlTaskCreateComponent />
  </Protector>
);

export default MlTaskCreate;
