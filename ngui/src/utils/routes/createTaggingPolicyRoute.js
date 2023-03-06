import { TAGGING_POLICY_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateTaggingPolicyRoute extends BaseRoute {
  page = "CreateOrganizationConstraint";

  link = TAGGING_POLICY_CREATE;
}

export default new CreateTaggingPolicyRoute();
