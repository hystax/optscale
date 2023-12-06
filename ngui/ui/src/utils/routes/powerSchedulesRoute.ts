import { POWER_SCHEDULES } from "urls";
import BaseRoute from "./baseRoute";

class PowerSchedulesRoute extends BaseRoute {
  page = "PowerSchedules";

  link = POWER_SCHEDULES;
}

export default new PowerSchedulesRoute();
