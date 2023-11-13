import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const CellValue = ({ expenses }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={expenses} />;

const totalExpenses = ({ totalTotalCostWithOffer }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_expenses">
      <FormattedMessage id="totalExpenses" />
    </TextWithDataTestId>
  ),
  accessorKey: "total_cost_with_offer",
  cell: ({ cell }) => <CellValue expenses={cell.getValue()} />,
  footer: () => <CellValue expenses={totalTotalCostWithOffer} />,
  defaultSort: "desc"
});

export default totalExpenses;
