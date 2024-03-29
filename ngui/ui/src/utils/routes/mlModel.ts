import { ML_MODEL } from "urls";
import BaseRoute from "./baseRoute";

class MlModelRoute extends BaseRoute {
  page = "MlModel";

  link = ML_MODEL;
}

export default new MlModelRoute();
