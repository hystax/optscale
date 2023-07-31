import { SETTINGS } from "urls";
import BaseRoute from "./baseRoute";

class SettingsRoute extends BaseRoute {
  page = "Settings";

  link = SETTINGS;
}

export default new SettingsRoute();
