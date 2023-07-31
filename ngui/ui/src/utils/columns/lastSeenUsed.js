import React from "react";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import { unixTimestampToDateTime } from "utils/datetime";

// TODO: could be merged with firstSeen column
const lastSeenUsed = ({ headerDataTestId, headerHelperMessageId } = {}) => ({
  header: (
    <HeaderHelperCell
      titleDataTestId={headerDataTestId}
      titleMessageId="lastSeenUsed"
      helperMessageId={headerHelperMessageId}
    />
  ),
  accessorKey: "last_used",
  cell: ({ cell }) => {
    const value = cell.getValue();

    return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
  }
});

export default lastSeenUsed;
