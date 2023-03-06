import { ML_MODELS_PARAMETER_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateMlApplicationParameterRoute extends BaseRoute {
  page = "CreateMlApplicationParameter";

  link = ML_MODELS_PARAMETER_CREATE;
}

export default new CreateMlApplicationParameterRoute();
