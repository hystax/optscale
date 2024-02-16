import Protector from "components/Protector";
import EditPowerScheduleContainer from "containers/EditPowerScheduleContainer";

const EditPowerSchedule = () => (
  <Protector allowedActions={["EDIT_PARTNER"]}>
    <EditPowerScheduleContainer />
  </Protector>
);

export default EditPowerSchedule;
