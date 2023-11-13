import HubOutlinedIcon from "@mui/icons-material/HubOutlined";
import { ML_RUN_BASE } from "urls";
import mlModelsRoute from "utils/routes/mlModelsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlModelsMenuItem extends BaseMenuItem {
  route = mlModelsRoute;

  messageId = "models";

  dataTestId = "btn_ml_models";

  icon = HubOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath.startsWith(`/${ML_RUN_BASE}/`);
}

export default new MlModelsMenuItem();
