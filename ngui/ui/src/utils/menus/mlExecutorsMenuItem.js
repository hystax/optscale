import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import mlExecutorsRoute from "utils/routes/mlExecutorsRoute";
import BaseMenuItem from "./baseMenuItem";

class MlExecutorsMenuItem extends BaseMenuItem {
  route = mlExecutorsRoute;

  messageId = "executors";

  dataTestId = "btn_ml_executors";

  icon = PlayCircleOutlineOutlinedIcon;
}

export default new MlExecutorsMenuItem();
