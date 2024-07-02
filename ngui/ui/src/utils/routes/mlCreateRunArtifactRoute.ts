import { ML_CREATE_RUN_ARTIFACT } from "urls";
import BaseRoute from "./baseRoute";

class MlCreateRunArtifactRoute extends BaseRoute {
  page = "MlCreateRunArtifact";

  link = ML_CREATE_RUN_ARTIFACT;
}

export default new MlCreateRunArtifactRoute();
