import HubOutlinedIcon from "@mui/icons-material/HubOutlined";
import { ML_RUN_BASE } from "urls";
import mlModelsRoute from "utils/routes/mlModelsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlModelsMenuItem extends BaseMenuItem {
  route = mlModelsRoute;

  messageId = "tasks";

  dataTestId = "btn_ml_tasks";

  icon = HubOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath.startsWith(`/${ML_RUN_BASE}/`);
}

export default new MlModelsMenuItem();
