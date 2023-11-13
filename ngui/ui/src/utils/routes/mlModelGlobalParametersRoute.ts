import { ML_MODELS_PARAMETERS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelGlobalParametersRoute extends BaseRoute {
  page = "MlModelGlobalParameters";

  link = ML_MODELS_PARAMETERS;
}

export default new MlModelGlobalParametersRoute();
