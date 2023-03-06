import { POOL_EXPENSES } from "urls";
import BaseRoute from "./baseRoute";

class PoolExpensesRoute extends BaseRoute {
  page = "PoolExpensesBreakdown";

  link = POOL_EXPENSES;
}

export default new PoolExpensesRoute();
