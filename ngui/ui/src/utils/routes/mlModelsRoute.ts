import { ML_MODELS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelsRoute extends BaseRoute {
  page = "MlModels";

  link = ML_MODELS;
}

export default new MlModelsRoute();
