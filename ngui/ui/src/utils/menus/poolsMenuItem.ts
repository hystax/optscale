import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import { ASSIGNMENT_RULE_CREATE, ASSIGNMENT_RULE } from "urls";
import { OPTSCALE_MODE } from "utils/constants";
import assignmentRulesRoute from "utils/routes/assignmentRulesRoute";
import pools from "utils/routes/poolsRoute";
import BaseMenuItem from "./baseMenuItem";

class PoolsMenuItem extends BaseMenuItem {
  route = pools;

  messageId = "pools";

  dataTestId = "btn_pools";

  dataProductTourId = PRODUCT_TOUR_IDS.POOLS;

  icon = CalculateOutlinedIcon;

  mode = OPTSCALE_MODE.FINOPS;

  isActive = (currentPath) =>
    currentPath.startsWith(this.route.link) ||
    currentPath.startsWith(ASSIGNMENT_RULE) ||
    currentPath.startsWith(assignmentRulesRoute.link) ||
    currentPath.startsWith(ASSIGNMENT_RULE_CREATE);
}

export default new PoolsMenuItem();
