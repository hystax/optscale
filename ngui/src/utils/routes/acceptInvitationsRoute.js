import { ACCEPT_INVITATIONS } from "urls";
import BaseRoute from "./baseRoute";

class AcceptInvitationsRoute extends BaseRoute {
  page = "AcceptInvitations";

  link = ACCEPT_INVITATIONS;

  layout = null;
}

export default new AcceptInvitationsRoute();
