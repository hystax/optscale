import { USER_MANAGEMENT } from "urls";
import BaseRoute from "./baseRoute";

class UsersRoute extends BaseRoute {
  page = "Employees";

  link = USER_MANAGEMENT;
}

export default new UsersRoute();
