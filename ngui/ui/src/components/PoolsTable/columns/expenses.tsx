import ExpensesTableHeader from "components/ExpensesTableHeader";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const expenses = ({ defaultSort, startDateTimestamp, endDateTimestamp } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_expenses">
      <ExpensesTableHeader startDateTimestamp={startDateTimestamp} endDateTimestamp={endDateTimestamp} />
    </TextWithDataTestId>
  ),
  accessorKey: "cost",
  cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue() ?? 0} />,
  defaultSort,
  columnSelector: {
    accessor: "cost",
    messageId: "expenses",
    dataTestId: "btn_toggle_cost",
  },
});

export default expenses;
