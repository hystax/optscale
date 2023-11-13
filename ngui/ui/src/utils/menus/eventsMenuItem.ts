import EventOutlined from "@mui/icons-material/EventOutlined";
import events from "utils/routes/eventsRoute";
import BaseMenuItem from "./baseMenuItem";

class EventsMenuItem extends BaseMenuItem {
  route = events;

  messageId = "events";

  dataTestId = "btn_events";

  icon = EventOutlined;
}

export default new EventsMenuItem();
