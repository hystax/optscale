import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import { PRODUCT_TOUR_IDS } from "components/Tour";
import { ENVIRONMENT_CREATE } from "urls";
import environments from "utils/routes/environmentsRoute";
import BaseMenuItem from "./baseMenuItem";

class EnvironmentsMenuItem extends BaseMenuItem {
  route = environments;

  messageId = "environments";

  dataTestId = "btn_environments";

  dataProductTourId = PRODUCT_TOUR_IDS.ENVIRONMENTS;

  icon = DnsOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath.startsWith(ENVIRONMENT_CREATE);
}

export default new EnvironmentsMenuItem();
