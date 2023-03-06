import { ML_MODELS_PARAMETER_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditMlApplicationParameterRoute extends BaseRoute {
  page = "EditMlApplicationParameter";

  link = ML_MODELS_PARAMETER_EDIT;
}

export default new EditMlApplicationParameterRoute();
