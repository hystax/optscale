import { ML_DATASETS } from "urls";
import BaseRoute from "./baseRoute";

class MlDatasetRoute extends BaseRoute {
  page = "MlDatasets";

  link = ML_DATASETS;
}

export default new MlDatasetRoute();
