import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { percentXofY } from "utils/math";

const CellValue = ({ savings, totalCostWithoutOffer }) => (
  <>
    <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={savings} />
    &nbsp;(
    <FormattedNumber value={percentXofY(savings, totalCostWithoutOffer)} format="percentage" />)
  </>
);

const savings = ({ totalTotalCostWithoutOffer, totalTotalCostWithOffer }) => ({
  id: "savings",
  header: (
    <TextWithDataTestId dataTestId="lbl_savings">
      <FormattedMessage id="savings" />
    </TextWithDataTestId>
  ),
  accessorFn: (originalRow) => originalRow.total_cost_without_offer - originalRow.total_cost_with_offer,
  cell: ({ cell, row: { original } }) => (
    <CellValue savings={cell.getValue()} totalCostWithoutOffer={original.total_cost_without_offer} />
  ),
  footer: () => {
    const value = totalTotalCostWithoutOffer - totalTotalCostWithOffer;
    return <CellValue savings={value} totalCostWithoutOffer={totalTotalCostWithoutOffer} />;
  }
});

export default savings;
