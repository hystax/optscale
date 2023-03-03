import { QUOTA_AND_BUDGET_CREATE } from "urls";
import BaseRoute from "./baseRoute";

class CreateQuotaAndBudgetPolicyRoute extends BaseRoute {
  page = "CreateOrganizationConstraint";

  link = QUOTA_AND_BUDGET_CREATE;
}

export default new CreateQuotaAndBudgetPolicyRoute();
