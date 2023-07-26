import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const formattedNumber = ({ headerMessageId, headerDataTestId, accessorKey, options = {}, fractionDigitsMax = 2 }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <FormattedNumber value={cell.getValue()} maximumFractionDigits={fractionDigitsMax} />,
  ...options
});

export default formattedNumber;
