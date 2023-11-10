import { ML_RUNSET_DETAILS } from "urls";
import BaseRoute from "./baseRoute";

class MlRunsetOverview extends BaseRoute {
  page = "MlRunsetOverview";

  link = ML_RUNSET_DETAILS;
}

export default new MlRunsetOverview();
