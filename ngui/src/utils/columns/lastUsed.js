import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { unixTimestampToDateTime } from "utils/datetime";

const lastUsed = ({ headerDataTestId, accessor = "last_used" }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="lastUsed" />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
});

export default lastUsed;
