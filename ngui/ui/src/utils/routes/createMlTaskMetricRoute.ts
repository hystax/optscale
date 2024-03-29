import { ML_TASK_METRIC_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateMlTaskMetricRoute extends BaseRoute {
  page = "CreateMlTaskMetric";

  link = ML_TASK_METRIC_CREATE;
}

export default new CreateMlTaskMetricRoute();
