import { ML_APPLICATIONS } from "urls";
import BaseRoute from "./baseRoute";

class MlApplicationsRoute extends BaseRoute {
  page = "MlApplications";

  link = ML_APPLICATIONS;
}

export default new MlApplicationsRoute();
