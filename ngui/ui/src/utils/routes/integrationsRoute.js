import { INTEGRATIONS } from "urls";
import BaseRoute from "./baseRoute";

class IntegrationsRoute extends BaseRoute {
  page = "Integrations";

  link = INTEGRATIONS;
}

export default new IntegrationsRoute();
