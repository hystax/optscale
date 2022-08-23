import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const savings = ({ headerDataTestId, headerMessageId = "possibleMonthlySavings", accessor = "saving", options = {} }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />,
  ...options
});

export default savings;
