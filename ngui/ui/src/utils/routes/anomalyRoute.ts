import { ANOMALY } from "urls";
import BaseRoute from "./baseRoute";

class AnomalyRoute extends BaseRoute {
  page = "OrganizationConstraint";

  link = ANOMALY;
}

export default new AnomalyRoute();
