import { JIRA_CONNECT } from "urls";
import BaseRoute from "./baseRoute";

class ConnectJiraRoute extends BaseRoute {
  page = "ConnectJira";

  link = JIRA_CONNECT;

  layout = null;
}

export default new ConnectJiraRoute();
