import { ANOMALY_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateAnomalyRoute extends BaseRoute {
  page = "CreateOrganizationConstraint";

  link = ANOMALY_CREATE;
}

export default new CreateAnomalyRoute();
