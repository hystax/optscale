import { ML_MODEL_DETAILS } from "urls";
import BaseRoute from "./baseRoute";

class MlModelDetailsRoute extends BaseRoute {
  page = "MlModelDetails";

  link = ML_MODEL_DETAILS;
}

export default new MlModelDetailsRoute();
