import { ML_TASK_DETAILS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelDetailsRoute extends BaseRoute {
  page = "MlModelDetails";

  link = ML_TASK_DETAILS;
}

export default new MlModelDetailsRoute();
