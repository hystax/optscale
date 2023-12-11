import { useCallback } from "react";
import { useIntl } from "react-intl";
import { INTERVAL_DURATION_VALUE_TYPES, formatIntervalDuration } from "utils/datetime";

export const useFormatIntervalDuration = () => {
  const intl = useIntl();

  return useCallback(
    ({ formatTo = Object.values(INTERVAL_DURATION_VALUE_TYPES), duration, precision = 2, compact = false }) =>
      formatIntervalDuration({
        formatTo,
        duration,
        precision,
        compact,
        intlFormatter: intl
      }),
    [intl]
  );
};
