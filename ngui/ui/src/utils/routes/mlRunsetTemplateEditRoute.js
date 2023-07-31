import { ML_EDIT_RUNSET_TEMPLATE } from "urls";
import BaseRoute from "./baseRoute";

class MlRunsetTemplateEditRoute extends BaseRoute {
  page = "MlRunsetTemplateEdit";

  link = ML_EDIT_RUNSET_TEMPLATE;
}

export default new MlRunsetTemplateEditRoute();
