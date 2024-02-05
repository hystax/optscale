import PoolExpenses from "components/PoolExpenses";
import TextWithDataTestId from "components/TextWithDataTestId";

const expenses = ({ defaultSort } = {}) => ({
  header: <TextWithDataTestId dataTestId="lbl_expenses" messageId="expensesThisMonth" />,
  accessorKey: "cost",
  cell: ({
    row: {
      original: { cost = 0, limit = 0 }
    }
  }) => <PoolExpenses limit={limit} cost={cost} />,
  defaultSort,
  columnSelector: {
    accessor: "cost",
    messageId: "expensesThisMonth",
    dataTestId: "btn_toggle_cost"
  }
});

export default expenses;
