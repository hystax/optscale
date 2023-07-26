import { CLOUD_EXPENSES } from "urls";
import BaseRoute from "./baseRoute";

class CloudExpensesRoute extends BaseRoute {
  page = "CloudExpensesBreakdown";

  link = CLOUD_EXPENSES;
}

export default new CloudExpensesRoute();
