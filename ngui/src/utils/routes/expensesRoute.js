import { EXPENSES } from "urls";
import BaseRoute from "./baseRoute";

class ExpensesRoute extends BaseRoute {
  page = "Expenses";

  link = EXPENSES;
}

export default new ExpensesRoute();
