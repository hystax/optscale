import { ML_MODEL_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlCreateModelRoute extends BaseRoute {
  page = "MlCreateModel";

  link = ML_MODEL_CREATE;
}

export default new MlCreateModelRoute();
