import { ML_APPLICATION_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class MlEditApplicationRoute extends BaseRoute {
  page = "MlEditApplication";

  link = ML_APPLICATION_EDIT;
}

export default new MlEditApplicationRoute();
