import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import { CLOUD_EXPENSES_BASE, POOL_EXPENSES_BASE, OWNER_EXPENSES_BASE } from "urls";
import { FILTER_BY } from "utils/constants";
import expenses from "utils/routes/expensesRoute";
import BaseMenuItem from "./baseMenuItem";

class ExpensesMenuItem extends BaseMenuItem {
  route = expenses;

  messageId = "costExplorerTitle";

  dataTestId = "btn_cost_explorer_page";

  icon = BarChartOutlinedIcon;

  isRootPath = (currentPath, currentQueryParams) =>
    currentPath === this.route.link && currentQueryParams[FILTER_BY] === undefined;

  isActive = (currentPath) =>
    currentPath === this.route.link ||
    currentPath.startsWith(`/${CLOUD_EXPENSES_BASE}`) ||
    currentPath.startsWith(`/${POOL_EXPENSES_BASE}`) ||
    currentPath.startsWith(`/${OWNER_EXPENSES_BASE}`);
}

export default new ExpensesMenuItem();
