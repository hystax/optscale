import { EXPENSES_MAP } from "urls";
import BaseRoute from "./baseRoute";

class ExpensesMapRoute extends BaseRoute {
  page = "ExpensesMap";

  link = EXPENSES_MAP;
}

export default new ExpensesMapRoute();
