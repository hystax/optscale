import { RESOURCE_ASSIGNMENT_RULE_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateResourceAssignmentRuleRoute extends BaseRoute {
  page = "CreateResourceAssignmentRule";

  link = RESOURCE_ASSIGNMENT_RULE_CREATE;
}

export default new CreateResourceAssignmentRuleRoute();
