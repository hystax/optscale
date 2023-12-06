import Mocked from "components/Mocked";
import { PowerScheduleDetailsMocked } from "components/PowerScheduleDetails";
import PowerScheduleDetailsContainer from "containers/PowerScheduleDetailsContainer";

const PowerScheduleDetails = () => (
  <Mocked mock={<PowerScheduleDetailsMocked />}>
    <PowerScheduleDetailsContainer />
  </Mocked>
);

export default PowerScheduleDetails;
