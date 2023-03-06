import { RESOURCE_LIFECYCLE } from "urls";
import BaseRoute from "./baseRoute";

class ResourceLifecycleRoute extends BaseRoute {
  page = "ResourceLifecycle";

  link = RESOURCE_LIFECYCLE;
}

export default new ResourceLifecycleRoute();
