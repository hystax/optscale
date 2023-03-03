import SyncAltOutlinedIcon from "@mui/icons-material/SyncAltOutlined";
import integrations from "utils/routes/integrationsRoute";
import BaseMenuItem from "./baseMenuItem";

class IntegrationsMenuItem extends BaseMenuItem {
  route = integrations;

  messageId = "integrations";

  dataTestId = "btn_integrations";

  icon = SyncAltOutlinedIcon;
}

export default new IntegrationsMenuItem();
