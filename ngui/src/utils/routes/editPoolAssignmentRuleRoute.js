import { POOL_ASSIGNMENT_RULE_EDIT } from "urls";
import BaseRoute from "./baseRoute";

class EditPoolAssignmentRuleRoute extends BaseRoute {
  page = "EditAssignmentRule";

  link = POOL_ASSIGNMENT_RULE_EDIT;
}

export default new EditPoolAssignmentRuleRoute();
