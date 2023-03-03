import { LIVE_DEMO } from "urls";
import BaseRoute from "./baseRoute";

class LiveDemoRoute extends BaseRoute {
  isTokenRequired = false;

  page = "LiveDemo";

  link = LIVE_DEMO;

  layout = null;
}

export default new LiveDemoRoute();
