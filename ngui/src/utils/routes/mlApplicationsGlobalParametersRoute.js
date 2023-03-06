import { ML_APPLICATIONS_PARAMETERS } from "urls";
import BaseRoute from "./baseRoute";

class MlApplicationsGlobalParametersRoute extends BaseRoute {
  page = "MlApplicationsGlobalParameters";

  link = ML_APPLICATIONS_PARAMETERS;
}

export default new MlApplicationsGlobalParametersRoute();
