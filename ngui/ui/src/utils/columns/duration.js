import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";
import { CELL_EMPTY_VALUE } from "utils/tables";

const Duration = ({ durationInSeconds }) => {
  const formatInterval = useFormatIntervalDuration();

  const intl = useIntl();

  return durationInSeconds === 0
    ? intl.formatMessage({ id: "xSeconds" }, { x: 0 })
    : formatInterval({
        formatTo: [
          INTERVAL_DURATION_VALUE_TYPES.WEEKS,
          INTERVAL_DURATION_VALUE_TYPES.DAYS,
          INTERVAL_DURATION_VALUE_TYPES.HOURS,
          INTERVAL_DURATION_VALUE_TYPES.MINUTES,
          INTERVAL_DURATION_VALUE_TYPES.SECONDS
        ],
        duration: intervalToDuration({
          start: 0,
          end: durationInSeconds * 1000
        })
      });
};

const duration = ({ headerMessageId, headerDataTestId, accessorKey, options = {} }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => {
    const durationInSeconds = cell.getValue();

    return durationInSeconds === 0 ? CELL_EMPTY_VALUE : <Duration durationInSeconds={durationInSeconds} />;
  },
  ...options
});

export default duration;
