import SettingsIcon from "@mui/icons-material/Settings";
import settings from "utils/routes/settingsRoute";
import BaseMenuItem from "./baseMenuItem";

class SettingsMenuItem extends BaseMenuItem {
  route = settings;

  messageId = "settings";

  dataTestId = "btn_settings";

  icon = SettingsIcon;
}

export default new SettingsMenuItem();
