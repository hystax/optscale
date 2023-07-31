import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import archivedRecommendationsRoute from "utils/routes/archivedRecommendationsRoute";
import recommendations from "utils/routes/recommendationsRoute";
import BaseMenuItem from "./baseMenuItem";

class RecommendationsMenuItem extends BaseMenuItem {
  route = recommendations;

  messageId = "recommendations";

  dataTestId = "btn_recommend";

  dataProductTourId = PRODUCT_TOUR_IDS.RECOMMENDATIONS;

  icon = ThumbUpAltOutlinedIcon;

  isActive = (currentPath) =>
    currentPath.startsWith(this.route.link) || currentPath.startsWith(archivedRecommendationsRoute.link);
}

export default new RecommendationsMenuItem();
