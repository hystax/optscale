import RunningWithErrorsOutlinedIcon from "@mui/icons-material/RunningWithErrorsOutlined";
import anomalies from "utils/routes/anomaliesRoute";
import BaseMenuItem from "./baseMenuItem";

class AnomaliesMenuItem extends BaseMenuItem {
  route = anomalies;

  messageId = "anomalyDetectionTitle";

  dataTestId = "btn_anomalies";

  icon = RunningWithErrorsOutlinedIcon;

  isActive = (currentPath) => currentPath.startsWith(this.route.link);
}

export default new AnomaliesMenuItem();
