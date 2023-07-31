import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const possibleMonthlySavings = ({ headerDataTestId, accessorKey = "saving", defaultSort }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="possibleMonthlySavings" />
    </TextWithDataTestId>
  ),
  accessorKey,
  defaultSort,
  cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
});

export default possibleMonthlySavings;
