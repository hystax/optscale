import { ML_MODELS_PARAMETER_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateMlModelParameterRoute extends BaseRoute {
  page = "CreateMlModelParameter";

  link = ML_MODELS_PARAMETER_CREATE;
}

export default new CreateMlModelParameterRoute();
