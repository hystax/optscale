import { ENVIRONMENTS } from "urls";
import BaseRoute from "./baseRoute";

class EnvironmentsRoute extends BaseRoute {
  page = "Environments";

  link = ENVIRONMENTS;
}

export default new EnvironmentsRoute();
