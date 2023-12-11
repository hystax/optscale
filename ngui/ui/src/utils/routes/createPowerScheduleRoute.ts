import { CREATE_POWER_SCHEDULE } from "urls";
import BaseRoute from "./baseRoute";

class CreatePowerScheduleRoute extends BaseRoute {
  page = "CreatePowerSchedule";

  link = CREATE_POWER_SCHEDULE;
}

export default new CreatePowerScheduleRoute();
