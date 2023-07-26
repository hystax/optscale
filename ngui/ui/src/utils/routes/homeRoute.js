import { HOME } from "urls";
import BaseRoute from "./baseRoute";

class HomeRoute extends BaseRoute {
  page = "Dashboard";

  link = HOME;
}

export default new HomeRoute();
