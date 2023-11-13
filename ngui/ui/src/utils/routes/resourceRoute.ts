import { RESOURCE } from "urls";
import BaseRoute from "./baseRoute";

class ResourceRoute extends BaseRoute {
  page = "Resource";

  link = RESOURCE;
}

export default new ResourceRoute();
