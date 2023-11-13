import { THEME_SETTINGS } from "urls";
import BaseRoute from "./baseRoute";

class ThemeSettingsRoute extends BaseRoute {
  page = "ThemeSettings";

  link = THEME_SETTINGS;
}

export default new ThemeSettingsRoute();
