import { useCallback } from "react";
import { useIntl } from "react-intl";
import { formatIntervalTimeAgo } from "utils/datetime";

export const useFormatIntervalTimeAgo = () => {
  const intl = useIntl();

  return useCallback(
    (agoSecondsTimestamp, precision) =>
      formatIntervalTimeAgo({
        agoSecondsTimestamp,
        precision,
        intlFormatter: intl
      }),
    [intl]
  );
};
