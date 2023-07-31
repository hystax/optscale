import { ARCHIVED_RECOMMENDATIONS } from "urls";
import BaseRoute from "./baseRoute";

class ArchivedRecommendationsRoute extends BaseRoute {
  page = "ArchivedRecommendations";

  link = ARCHIVED_RECOMMENDATIONS;
}

export default new ArchivedRecommendationsRoute();
