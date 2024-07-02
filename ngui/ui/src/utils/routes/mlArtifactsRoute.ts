import { ML_ARTIFACTS } from "urls";
import BaseRoute from "./baseRoute";

class MlArtifactsRoute extends BaseRoute {
  page = "MlArtifacts";

  link = ML_ARTIFACTS;
}

export default new MlArtifactsRoute();
