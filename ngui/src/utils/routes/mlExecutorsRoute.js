import { ML_EXECUTORS } from "urls";
import BaseRoute from "./baseRoute";

class MlExecutorsRoute extends BaseRoute {
  page = "MlExecutors";

  link = ML_EXECUTORS;
}

export default new MlExecutorsRoute();
