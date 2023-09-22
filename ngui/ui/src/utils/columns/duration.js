import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedDuration from "components/FormattedDuration";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const duration = ({ headerMessageId, headerDataTestId, accessorKey, options = {} }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => {
    const durationInSeconds = cell.getValue();

    return durationInSeconds === 0 ? CELL_EMPTY_VALUE : <FormattedDuration durationInSeconds={durationInSeconds} />;
  },
  ...options
});

export default duration;
