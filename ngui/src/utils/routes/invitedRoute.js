import { INVITED } from "urls";
import BaseRoute from "./baseRoute";

class InvitedRoute extends BaseRoute {
  isTokenRequired = false;

  page = "Invited";

  link = INVITED;

  layout = null;
}

export default new InvitedRoute();
