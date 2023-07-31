import { ML_RUNSET_TEMPLATE_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlRunsetTemplateCreateRoute extends BaseRoute {
  page = "MlRunsetTemplateCreate";

  link = ML_RUNSET_TEMPLATE_CREATE;
}

export default new MlRunsetTemplateCreateRoute();
