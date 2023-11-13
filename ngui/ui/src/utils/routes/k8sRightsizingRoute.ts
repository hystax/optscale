import { K8S_RIGHTSIZING } from "urls";
import BaseRoute from "./baseRoute";

class K8sRightsizingRoute extends BaseRoute {
  page = "K8sRightsizing";

  link = K8S_RIGHTSIZING;
}

export default new K8sRightsizingRoute();
