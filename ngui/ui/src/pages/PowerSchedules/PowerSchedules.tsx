import Mocked from "components/Mocked";
import { PowerSchedulesMocked } from "components/PowerSchedules";
import PowerSchedulesContainer from "containers/PowerSchedulesContainer";

const PowerSchedules = () => (
  <Mocked mock={<PowerSchedulesMocked />}>
    <PowerSchedulesContainer />
  </Mocked>
);

export default PowerSchedules;
