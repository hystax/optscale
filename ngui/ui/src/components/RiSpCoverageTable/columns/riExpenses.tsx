import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { percentXofY } from "utils/math";

const CellValue = ({ expenses, totalExpenses }) => (
  <>
    <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={expenses} />
    &nbsp; (<FormattedNumber value={percentXofY(expenses, totalExpenses)} format="percentage" />)
  </>
);

const riExpenses = ({ totalRiCostWithOffer, totalTotalCostWithOffer }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_ri_expenses">
      <FormattedMessage id="riExpenses" />
    </TextWithDataTestId>
  ),
  accessorKey: "ri_cost_with_offer",
  cell: ({
    cell,
    row: {
      original: { total_cost_with_offer: totalExpenses }
    }
  }) => <CellValue expenses={cell.getValue()} totalExpenses={totalExpenses} />,
  footer: () => <CellValue expenses={totalRiCostWithOffer} totalExpenses={totalTotalCostWithOffer} />
});

export default riExpenses;
