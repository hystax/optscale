import { ML_TASKS } from "urls";
import BaseRoute from "./baseRoute";

class MlTasksRoute extends BaseRoute {
  page = "MlTasks";

  link = ML_TASKS;
}

export default new MlTasksRoute();
