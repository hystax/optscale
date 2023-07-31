import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { unixTimestampToDateTime } from "utils/datetime";

// TODO: could be merged with firstSeen column
const firstSeenOn = ({ headerDataTestId } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="firstSeenOn" />
    </TextWithDataTestId>
  ),
  accessorKey: "first_seen",
  cell: ({ cell }) => {
    const value = cell.getValue();

    return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
  }
});

export default firstSeenOn;
