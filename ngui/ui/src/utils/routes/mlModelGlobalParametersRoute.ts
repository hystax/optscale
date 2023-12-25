import { ML_TASK_PARAMETERS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelGlobalParametersRoute extends BaseRoute {
  page = "MlModelGlobalParameters";

  link = ML_TASK_PARAMETERS;
}

export default new MlModelGlobalParametersRoute();
