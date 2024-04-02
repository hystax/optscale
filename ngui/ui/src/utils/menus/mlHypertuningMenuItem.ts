import TuneOutlinedIcon from "@mui/icons-material/TuneOutlined";
import { ML_RUNSETS_BASE } from "urls";
import mlRunsetsRoute from "utils/routes/mlRunsetsRoute";
import BaseMenuItem from "./baseMenuItem";

class HypertuningMenuItem extends BaseMenuItem {
  route = mlRunsetsRoute;

  messageId = "hypertuning";

  dataTestId = "btn_ml_runsets";

  icon = TuneOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link) || currentPath.startsWith(`/${ML_RUNSETS_BASE}`);
}

export default new HypertuningMenuItem();
