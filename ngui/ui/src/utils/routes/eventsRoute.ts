import { EVENTS } from "urls";
import BaseRoute from "./baseRoute";

class EventsRoute extends BaseRoute {
  page = "Events";

  link = EVENTS;
}

export default new EventsRoute();
