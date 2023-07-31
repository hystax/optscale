import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { percentXofY } from "utils/math";

const CellValue = ({ expenses, totalExpenses }) => (
  <>
    <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={expenses} />
    &nbsp;(
    <FormattedNumber value={percentXofY(expenses, totalExpenses)} format="percentage" />)
  </>
);

const spExpenses = ({ totalSpCostWithOffer, totalTotalCostWithOffer }) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_sp_expenses">
      <FormattedMessage id="spExpenses" />
    </TextWithDataTestId>
  ),
  accessorKey: "sp_cost_with_offer",
  cell: ({
    cell,
    row: {
      original: { total_cost_with_offer: totalExpenses }
    }
  }) => <CellValue expenses={cell.getValue()} totalExpenses={totalExpenses} />,
  footer: () => <CellValue expenses={totalSpCostWithOffer} totalExpenses={totalTotalCostWithOffer} />
});

export default spExpenses;
