import { ML_DATASET_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class MlDatasetCreateRoute extends BaseRoute {
  page = "MlDatasetCreate";

  link = ML_DATASET_CREATE;
}

export default new MlDatasetCreateRoute();
