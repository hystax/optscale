import { ML_TASKS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelsRoute extends BaseRoute {
  page = "MlModels";

  link = ML_TASKS;
}

export default new MlModelsRoute();
