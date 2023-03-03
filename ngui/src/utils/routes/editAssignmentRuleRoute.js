import { ASSIGNMENT_RULE_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditAssignmentRuleRoute extends BaseRoute {
  page = "EditAssignmentRule";

  link = ASSIGNMENT_RULE_EDIT;
}

export default new EditAssignmentRuleRoute();
