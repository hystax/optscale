import { ML_METRIC_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateMlMetricRoute extends BaseRoute {
  page = "CreateMlMetric";

  link = ML_METRIC_CREATE;
}

export default new CreateMlMetricRoute();
