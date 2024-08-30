import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import { OPTSCALE_MODE } from "utils/constants";
import recommendations from "utils/routes/recommendationsRoute";
import BaseMenuItem from "./baseMenuItem";

class RecommendationsMenuItem extends BaseMenuItem {
  route = recommendations;

  messageId = "recommendations";

  dataTestId = "btn_recommend";

  dataProductTourId = PRODUCT_TOUR_IDS.RECOMMENDATIONS;

  icon = ThumbUpAltOutlinedIcon;

  mode = OPTSCALE_MODE.FINOPS;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new RecommendationsMenuItem();
