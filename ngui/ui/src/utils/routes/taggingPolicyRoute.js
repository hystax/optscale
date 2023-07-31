import { TAGGING_POLICY } from "urls";
import BaseRoute from "./baseRoute";

class TaggingPolicyRoute extends BaseRoute {
  page = "OrganizationConstraint";

  link = TAGGING_POLICY;
}

export default new TaggingPolicyRoute();
