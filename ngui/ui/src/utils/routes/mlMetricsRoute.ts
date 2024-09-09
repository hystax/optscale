import { ML_METRICS } from "urls";
import BaseRoute from "./baseRoute";

class MlMetricsRoute extends BaseRoute {
  page = "MlMetrics";

  link = ML_METRICS;
}

export default new MlMetricsRoute();
