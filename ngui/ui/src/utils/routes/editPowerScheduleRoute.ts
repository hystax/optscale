import { EDIT_POWER_SCHEDULE } from "urls";
import BaseRoute from "./baseRoute";

class EditPowerScheduleRoute extends BaseRoute {
  page = "EditPowerSchedule";

  link = EDIT_POWER_SCHEDULE;
}

export default new EditPowerScheduleRoute();
