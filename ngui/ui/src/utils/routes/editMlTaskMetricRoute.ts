import { ML_TASK_METRIC_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditMlTaskMetricRoute extends BaseRoute {
  page = "EditMlTaskMetric";

  link = ML_TASK_METRIC_EDIT;
}

export default new EditMlTaskMetricRoute();
