import { LOGIN } from "urls";
import BaseRoute from "./baseRoute";

class LoginRoute extends BaseRoute {
  isTokenRequired = false;

  page = "Authorization";

  link = LOGIN;

  layout = null;
}

export default new LoginRoute();
