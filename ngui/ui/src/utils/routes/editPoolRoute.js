import { POOL_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditPoolRoute extends BaseRoute {
  page = "EditPool";

  link = POOL_EDIT;
}

export default new EditPoolRoute();
