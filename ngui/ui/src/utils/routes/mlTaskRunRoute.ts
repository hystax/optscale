import { ML_TASK_RUN } from "urls";
import BaseRoute from "./baseRoute";

class MlTaskRun extends BaseRoute {
  page = "MlTaskRun";

  link = ML_TASK_RUN;
}

export default new MlTaskRun();
