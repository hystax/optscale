import CreatePowerScheduleComponent from "components/CreatePowerSchedule";
import Protector from "components/Protector";

const CreatePowerSchedule = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <CreatePowerScheduleComponent />
  </Protector>
);

export default CreatePowerSchedule;
