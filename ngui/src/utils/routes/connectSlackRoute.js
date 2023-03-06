import { SLACK_CONNECT } from "urls";
import BaseRoute from "./baseRoute";

class ConnectSlackRoute extends BaseRoute {
  page = "ConnectSlack";

  link = SLACK_CONNECT;

  layout = null;
}

export default new ConnectSlackRoute();
