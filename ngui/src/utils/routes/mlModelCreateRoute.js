import { ML_APPLICATION_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlModelCreateRoute extends BaseRoute {
  page = "MlModelCreate";

  link = ML_APPLICATION_CREATE;
}

export default new MlModelCreateRoute();
