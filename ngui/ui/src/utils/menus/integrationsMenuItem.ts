import SyncAltOutlinedIcon from "@mui/icons-material/SyncAltOutlined";
import { BI_EXPORTS } from "urls";
import { OPTSCALE_MODE } from "utils/constants";
import integrations from "utils/routes/integrationsRoute";
import BaseMenuItem from "./baseMenuItem";

class IntegrationsMenuItem extends BaseMenuItem {
  route = integrations;

  messageId = "integrations";

  dataTestId = "btn_integrations";

  icon = SyncAltOutlinedIcon;

  mode = OPTSCALE_MODE.FINOPS;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath.startsWith(BI_EXPORTS);
}

export default new IntegrationsMenuItem();
