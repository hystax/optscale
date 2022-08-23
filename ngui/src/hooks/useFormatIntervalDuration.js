import { useIntl } from "react-intl";
import { INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";
import { capitalize } from "utils/strings";

export const useFormatIntervalDuration = () => {
  const intl = useIntl();

  return ({ formatTo = Object.values(INTERVAL_DURATION_VALUE_TYPES), duration, precision = 2 }) =>
    formatTo
      .filter((type) => Boolean(duration[type]))
      .slice(0, precision)
      .map((type) => intl.formatMessage({ id: `x${capitalize(type)}` }, { x: duration[type] }))
      .join(", ");
};
