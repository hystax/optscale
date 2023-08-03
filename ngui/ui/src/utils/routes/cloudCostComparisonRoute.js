import { CLOUD_COST_COMPARISON } from "urls";
import BaseRoute from "./baseRoute";

class CloudCostComparisonRoute extends BaseRoute {
  page = "CloudCostComparison";

  link = CLOUD_COST_COMPARISON;
}

export default new CloudCostComparisonRoute();
