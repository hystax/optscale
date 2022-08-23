import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const possibleMonthlySavings = ({ headerDataTestId, accessor = "saving", defaultSort }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="possibleMonthlySavings" />
    </TextWithDataTestId>
  ),
  accessor,
  defaultSort,
  Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
});

export default possibleMonthlySavings;
