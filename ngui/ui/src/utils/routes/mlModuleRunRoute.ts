import { ML_MODEL_RUN } from "urls";
import BaseRoute from "./baseRoute";

class MlModelRun extends BaseRoute {
  page = "MlModelRun";

  link = ML_MODEL_RUN;
}

export default new MlModelRun();
