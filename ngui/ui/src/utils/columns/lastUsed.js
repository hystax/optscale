import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { unixTimestampToDateTime } from "utils/datetime";

const lastUsed = ({
  id = "last_used",
  headerDataTestId = "last_used_label",
  accessorKey = "last_used",
  accessorFn,
  defaultSort
} = {}) => ({
  id,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="lastUsed" />
    </TextWithDataTestId>
  ),
  accessorKey,
  accessorFn,
  defaultSort,
  cell: ({ cell }) => {
    const value = cell.getValue();

    return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
  }
});

export default lastUsed;
