import { useIntl } from "react-intl";
import { secondsToMilliseconds, intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";
import { useFormatIntervalDuration } from "./useFormatIntervalDuration";

export const useIntervalTimeAgo = (agoSecondsTimestamp, precision) => {
  const intl = useIntl();

  const duration = intervalToDuration({ start: +new Date(), end: secondsToMilliseconds(agoSecondsTimestamp) });

  const format = useFormatIntervalDuration();

  const agoIntervalString = format({
    formatTo: [
      INTERVAL_DURATION_VALUE_TYPES.WEEKS,
      INTERVAL_DURATION_VALUE_TYPES.DAYS,
      INTERVAL_DURATION_VALUE_TYPES.HOURS,
      INTERVAL_DURATION_VALUE_TYPES.MINUTES,
      INTERVAL_DURATION_VALUE_TYPES.SECONDS
    ],
    duration,
    precision
  });

  return `${agoIntervalString} ${intl.formatMessage({ id: "ago" })}`;
};
