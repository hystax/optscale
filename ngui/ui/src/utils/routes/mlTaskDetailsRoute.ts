import { ML_TASK_DETAILS } from "urls";
import BaseRoute from "./baseRoute";

class MlTaskDetailsRoute extends BaseRoute {
  page = "MlTaskDetails";

  link = ML_TASK_DETAILS;
}

export default new MlTaskDetailsRoute();
