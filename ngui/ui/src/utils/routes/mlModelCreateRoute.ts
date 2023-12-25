import { ML_TASK_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlModelCreateRoute extends BaseRoute {
  page = "MlModelCreate";

  link = ML_TASK_CREATE;
}

export default new MlModelCreateRoute();
