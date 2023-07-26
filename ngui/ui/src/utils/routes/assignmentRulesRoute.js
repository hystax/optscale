import { ASSIGNMENT_RULES } from "urls";
import BaseRoute from "./baseRoute";

class AssignmentRulesRoute extends BaseRoute {
  page = "AssignmentRules";

  link = ASSIGNMENT_RULES;
}

export default new AssignmentRulesRoute();
