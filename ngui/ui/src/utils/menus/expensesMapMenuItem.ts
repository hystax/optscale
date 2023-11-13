import PublicOutlinedIcon from "@mui/icons-material/PublicOutlined";
import expensesMap from "utils/routes/expensesMapRoute";
import BaseMenuItem from "./baseMenuItem";

class ExpensesMapMenuItem extends BaseMenuItem {
  route = expensesMap;

  messageId = "costMapTitle";

  dataTestId = "btn_cost_map";

  icon = PublicOutlinedIcon;
}

export default new ExpensesMapMenuItem();
