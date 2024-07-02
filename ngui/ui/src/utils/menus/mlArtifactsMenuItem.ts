import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import mlArtifactsRoute from "utils/routes/mlArtifactsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlArtifactsMenuItem extends BaseMenuItem {
  route = mlArtifactsRoute;

  messageId = "artifacts";

  dataTestId = "btn_ml_artifacts";

  icon = DescriptionOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new MlArtifactsMenuItem();
