import { ML_TASK_RUN } from "urls";
import BaseRoute from "./baseRoute";

class MlModelRun extends BaseRoute {
  page = "MlModelRun";

  link = ML_TASK_RUN;
}

export default new MlModelRun();
