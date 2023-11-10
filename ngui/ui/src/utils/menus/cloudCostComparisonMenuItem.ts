import CompareOutlinedIcon from "@mui/icons-material/CompareOutlined";
import cloudCostComparisonRoute from "utils/routes/cloudCostComparisonRoute";
import BaseMenuItem from "./baseMenuItem";

class CloudCostComparisonMenuItem extends BaseMenuItem {
  route = cloudCostComparisonRoute;

  messageId = "costComparisonTitle";

  dataTestId = "btn_cost_comparison";

  icon = CompareOutlinedIcon;
}

export default new CloudCostComparisonMenuItem();
