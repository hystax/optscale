import { ML_RUNSET_TEMPLATES } from "urls";
import BaseRoute from "./baseRoute";

class MlRunsetsRoute extends BaseRoute {
  page = "MlRunsets";

  link = ML_RUNSET_TEMPLATES;
}

export default new MlRunsetsRoute();
