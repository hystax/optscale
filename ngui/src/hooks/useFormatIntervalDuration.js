import { useCallback } from "react";
import { useIntl } from "react-intl";
import { INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";
import { capitalize } from "utils/strings";

export const useFormatIntervalDuration = () => {
  const intl = useIntl();

  return useCallback(
    ({ formatTo = Object.values(INTERVAL_DURATION_VALUE_TYPES), duration, precision = 2, compact = false }) => {
      const timeFrames = formatTo.filter((type) => Boolean(duration[type])).slice(0, precision);

      if (compact) {
        return timeFrames
          .map((type) => intl.formatMessage({ id: `x${capitalize(type)}Compact` }, { x: duration[type] }))
          .join(" ");
      }

      return timeFrames.map((type) => intl.formatMessage({ id: `x${capitalize(type)}` }, { x: duration[type] })).join(", ");
    },
    [intl]
  );
};
