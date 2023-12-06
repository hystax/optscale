import { POWER_SCHEDULE_DETAILS } from "urls";
import BaseRoute from "./baseRoute";

class PowerScheduleDetailsRoute extends BaseRoute {
  page = "PowerScheduleDetails";

  link = POWER_SCHEDULE_DETAILS;
}

export default new PowerScheduleDetailsRoute();
