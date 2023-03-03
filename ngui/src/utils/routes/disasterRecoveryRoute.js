import { DISASTER_RECOVERY } from "urls";
import BaseRoute from "./baseRoute";

class DisasterRecoveryRoute extends BaseRoute {
  page = "DisasterRecovery";

  link = DISASTER_RECOVERY;
}

export default new DisasterRecoveryRoute();
