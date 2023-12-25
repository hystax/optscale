import { ML_DATASET_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class MlDatasetCreateRoute extends BaseRoute {
  page = "MlDatasetEdit";

  link = ML_DATASET_EDIT;
}

export default new MlDatasetCreateRoute();
