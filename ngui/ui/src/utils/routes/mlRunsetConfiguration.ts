import { ML_RUNSET_TEMPLATE_CONFIGURATION } from "urls";
import BaseRoute from "./baseRoute";

class MlRunsetConfiguration extends BaseRoute {
  page = "MlRunsetConfiguration";

  link = ML_RUNSET_TEMPLATE_CONFIGURATION;
}

export default new MlRunsetConfiguration();
