import { ASSIGNMENT_RULE_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateAssignmentRuleRoute extends BaseRoute {
  page = "CreateAssignmentRule";

  link = ASSIGNMENT_RULE_CREATE;
}

export default new CreateAssignmentRuleRoute();
