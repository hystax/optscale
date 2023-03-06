import HubOutlinedIcon from "@mui/icons-material/HubOutlined";
import mlApplicationsRoute from "utils/routes/mlApplicationsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlApplicationsMenuItem extends BaseMenuItem {
  route = mlApplicationsRoute;

  messageId = "applications";

  dataTestId = "btn_ml_applications";

  icon = HubOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new MlApplicationsMenuItem();
