import { ML_TASK_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlTaskCreateRoute extends BaseRoute {
  page = "MlTaskCreate";

  link = ML_TASK_CREATE;
}

export default new MlTaskCreateRoute();
