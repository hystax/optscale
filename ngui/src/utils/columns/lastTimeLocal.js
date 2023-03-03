import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const lastTimeLocal = ({ headerDataTestId, messageId, accessorKey, style = {} }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  style,
  cell: ({ cell }) => {
    const value = cell.getValue();

    return value === 0 ? <FormattedMessage id="never" /> : format(secondsToMilliseconds(value), EN_FULL_FORMAT);
  }
});

export default lastTimeLocal;
