import { TAGGING_POLICIES } from "urls";
import BaseRoute from "./baseRoute";

class TaggingPoliciesRoute extends BaseRoute {
  page = "TaggingPolicies";

  link = TAGGING_POLICIES;
}

export default new TaggingPoliciesRoute();
