import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
import mlMetricsRoute from "utils/routes/mlMetricsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlTasksMenuItem extends BaseMenuItem {
  route = mlMetricsRoute;

  messageId = "metrics";

  dataTestId = "btn_ml_metrics";

  icon = TrendingUpOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new MlTasksMenuItem();
