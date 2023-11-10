import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { CELL_EMPTY_VALUE } from "utils/tables";

const poolLimit = () => ({
  header: <TextWithDataTestId dataTestId="lbl_limit" messageId="limit" />,
  accessorKey: "limit",
  cell: ({
    cell,
    row: {
      original: { hasLimit }
    }
  }) => (hasLimit ? <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue() || 0} /> : CELL_EMPTY_VALUE),
  columnSelector: {
    accessor: "limit",
    messageId: "limit",
    dataTestId: "btn_toggle_limit"
  }
});

export default poolLimit;
