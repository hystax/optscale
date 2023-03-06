import CurrencyExchangeOutlinedIcon from "@mui/icons-material/CurrencyExchangeOutlined";
import quotas from "utils/routes/quotasRoute";
import BaseMenuItem from "./baseMenuItem";

class QuotasMenuItem extends BaseMenuItem {
  route = quotas;

  messageId = "quotasAndBudgetsTitle";

  dataTestId = "btn_quotas_and_budgets";

  isActive = (currentPath) => currentPath.startsWith(this.route.link);

  icon = CurrencyExchangeOutlinedIcon;
}

export default new QuotasMenuItem();
