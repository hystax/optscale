import { RESET_PASSWORD } from "urls";
import BaseRoute from "./baseRoute";

class ResetPasswordRoute extends BaseRoute {
  isTokenRequired = false;

  page = "ResetPassword";

  link = RESET_PASSWORD;

  layout = null;
}

export default new ResetPasswordRoute();
