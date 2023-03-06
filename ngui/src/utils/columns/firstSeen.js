import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { unixTimestampToDateTime } from "utils/datetime";

const firstSeen = ({ id = "first_seen", headerDataTestId, accessorKey, accessorFn } = {}) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="firstSeen" />
    </TextWithDataTestId>
  ),
  accessorKey,
  accessorFn,
  cell: ({ cell }) => (cell.getValue() === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(cell.getValue()))
});

export default firstSeen;
