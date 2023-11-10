import { OWNER_EXPENSES } from "urls";
import BaseRoute from "./baseRoute";

class OwnerExpensesRoute extends BaseRoute {
  page = "OwnerExpensesBreakdown";

  link = OWNER_EXPENSES;
}

export default new OwnerExpensesRoute();
