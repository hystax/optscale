import { POOL_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreatePoolRoute extends BaseRoute {
  page = "CreatePool";

  link = POOL_CREATE;
}

export default new CreatePoolRoute();
