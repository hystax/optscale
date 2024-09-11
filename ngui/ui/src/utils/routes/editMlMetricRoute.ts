import { ML_METRIC_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditMlMetricRoute extends BaseRoute {
  page = "EditMlMetric";

  link = ML_METRIC_EDIT;
}

export default new EditMlMetricRoute();
