import { QUOTAS_AND_BUDGETS } from "urls";
import BaseRoute from "./baseRoute";

class QuotasRoute extends BaseRoute {
  page = "QuotasAndBudgets";

  link = QUOTAS_AND_BUDGETS;
}

export default new QuotasRoute();
