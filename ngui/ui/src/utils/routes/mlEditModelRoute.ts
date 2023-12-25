import { ML_TASK_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class MlEditModelRoute extends BaseRoute {
  page = "MlEditModel";

  link = ML_TASK_EDIT;
}

export default new MlEditModelRoute();
