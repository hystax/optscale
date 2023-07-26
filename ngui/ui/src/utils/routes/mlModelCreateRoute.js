import { ML_MODEL_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlModelCreateRoute extends BaseRoute {
  page = "MlModelCreate";

  link = ML_MODEL_CREATE;
}

export default new MlModelCreateRoute();
