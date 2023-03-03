import { REGISTER } from "urls";
import BaseRoute from "./baseRoute";

class RegisterRoute extends BaseRoute {
  isTokenRequired = false;

  page = "Authorization";

  link = REGISTER;

  layout = null;
}

export default new RegisterRoute();
