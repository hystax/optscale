import { CLUSTER_TYPES } from "urls";
import BaseRoute from "./baseRoute";

class ClusterTypesRoute extends BaseRoute {
  page = "ClusterTypes";

  link = CLUSTER_TYPES;
}

export default new ClusterTypesRoute();
