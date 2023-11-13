import RestoreOutlinedIcon from "@mui/icons-material/RestoreOutlined";
import archivedRecommendationsRoute from "utils/routes/archivedRecommendationsRoute";
import BaseMenuItem from "./baseMenuItem";

class RecommendationsArchiveMenuItem extends BaseMenuItem {
  route = archivedRecommendationsRoute;

  messageId = "archive";

  dataTestId = "btn_recommend_archive";

  icon = RestoreOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new RecommendationsArchiveMenuItem();
