import { CLUSTER_TYPE_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateClusterTypeRoute extends BaseRoute {
  page = "CreateClusterType";

  link = CLUSTER_TYPE_CREATE;
}

export default new CreateClusterTypeRoute();
