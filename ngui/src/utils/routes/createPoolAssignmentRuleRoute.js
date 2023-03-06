import { POOL_ASSIGNMENT_RULE_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreatePoolAssignmentRuleRoute extends BaseRoute {
  page = "CreateAssignmentRule";

  link = POOL_ASSIGNMENT_RULE_CREATE;
}

export default new CreatePoolAssignmentRuleRoute();
