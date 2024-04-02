import { ML_TASK_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class MlEditTaskRoute extends BaseRoute {
  page = "MlEditTask";

  link = ML_TASK_EDIT;
}

export default new MlEditTaskRoute();
