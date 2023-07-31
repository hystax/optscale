import { ENVIRONMENT_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateEnvironmentRoute extends BaseRoute {
  page = "CreateEnvironment";

  link = ENVIRONMENT_CREATE;
}

export default new CreateEnvironmentRoute();
