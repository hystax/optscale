import { EMPLOYEES_INVITE } from "urls";
import BaseRoute from "./baseRoute";

class InviteEmployeesRoute extends BaseRoute {
  page = "InviteEmployees";

  link = EMPLOYEES_INVITE;
}

export default new InviteEmployeesRoute();
