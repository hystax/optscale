import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const usage = ({ headerDataTestId, headerMessageId, accessorKey = "usage" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  cell: ({ cell }) => (
    <FormattedMessage id="xHours" values={{ x: <FormattedNumber value={cell.getValue()} maximumFractionDigits={2} /> }} />
  ),
  accessorKey
});

export default usage;
