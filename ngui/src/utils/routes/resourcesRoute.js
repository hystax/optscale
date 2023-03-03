import { RESOURCES } from "urls";
import BaseRoute from "./baseRoute";

class ResourcesRoute extends BaseRoute {
  page = "Resources";

  link = RESOURCES;
}

export default new ResourcesRoute();
