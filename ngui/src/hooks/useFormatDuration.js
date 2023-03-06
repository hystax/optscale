import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

export const useFormatDuration = (value, noValueResult = "-") => {
  const formatInterval = useFormatIntervalDuration();

  if (!value) return noValueResult;

  const measure = intervalToDuration({
    start: 0,
    end: value
  });

  return formatInterval({
    formatTo: [
      INTERVAL_DURATION_VALUE_TYPES.WEEKS,
      INTERVAL_DURATION_VALUE_TYPES.DAYS,
      INTERVAL_DURATION_VALUE_TYPES.HOURS,
      INTERVAL_DURATION_VALUE_TYPES.MINUTES
    ],
    duration: measure
  });
};
