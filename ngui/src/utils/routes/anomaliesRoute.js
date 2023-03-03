import { ANOMALIES } from "urls";
import BaseRoute from "./baseRoute";

class AnomaliesRoute extends BaseRoute {
  page = "Anomalies";

  link = ANOMALIES;
}

export default new AnomaliesRoute();
