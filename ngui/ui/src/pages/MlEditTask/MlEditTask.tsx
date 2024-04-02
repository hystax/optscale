import Protector from "components/Protector";
import MlEditTaskContainer from "containers/MlEditTaskContainer";

const MlEditTask = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <MlEditTaskContainer />
  </Protector>
);

export default MlEditTask;
