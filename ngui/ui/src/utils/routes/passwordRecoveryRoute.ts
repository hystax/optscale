import { PASSWORD_RECOVERY } from "urls";
import BaseRoute from "./baseRoute";

class PasswordRecoveryRoute extends BaseRoute {
  isTokenRequired = false;

  page = "PasswordRecovery";

  link = PASSWORD_RECOVERY;

  layout = null;
}

export default new PasswordRecoveryRoute();
