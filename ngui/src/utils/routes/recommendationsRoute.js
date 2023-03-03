import { RECOMMENDATIONS } from "urls";
import BaseRoute from "./baseRoute";

class RecommendationsRoute extends BaseRoute {
  page = "Recommendations";

  link = RECOMMENDATIONS;
}

export default new RecommendationsRoute();
