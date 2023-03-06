import { ACCEPT_INVITATION } from "urls";
import BaseRoute from "./baseRoute";

class AcceptInvitationRoute extends BaseRoute {
  page = "AcceptInvitation";

  link = ACCEPT_INVITATION;

  layout = null;
}

export default new AcceptInvitationRoute();
