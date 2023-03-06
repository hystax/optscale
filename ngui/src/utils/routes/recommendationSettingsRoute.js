import { RECOMMENDATION_SETTINGS } from "urls";
import BaseRoute from "./baseRoute";

class RecommendationSettingsRoute extends BaseRoute {
  page = "RecommendationSettings";

  link = RECOMMENDATION_SETTINGS;
}

export default new RecommendationSettingsRoute();
