import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { hasLimit } from "utils/pools";
import { CELL_EMPTY_VALUE } from "utils/tables";

const poolLimit = () => ({
  header: <TextWithDataTestId dataTestId="lbl_limit" messageId="limit" />,
  accessorKey: "limit",
  cell: ({ cell }) => {
    const limit = cell.getValue();
    return hasLimit(limit) ? <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={limit} /> : CELL_EMPTY_VALUE;
  },
  columnSelector: {
    accessor: "limit",
    messageId: "limit",
    dataTestId: "btn_toggle_limit"
  }
});

export default poolLimit;
