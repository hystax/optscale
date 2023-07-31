import { ML_MODEL_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class MlEditModelRoute extends BaseRoute {
  page = "MlEditModel";

  link = ML_MODEL_EDIT;
}

export default new MlEditModelRoute();
