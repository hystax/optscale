import { ML_TASK_METRICS } from "urls";
import BaseRoute from "./baseRoute";

class MlTaskGlobalMetricsRoute extends BaseRoute {
  page = "MlTaskGlobalMetrics";

  link = ML_TASK_METRICS;
}

export default new MlTaskGlobalMetricsRoute();
