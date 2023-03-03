import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

const MlRunDuration = ({ durationInSeconds }) => {
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

MlRunDuration.propTypes = {
  durationInSeconds: PropTypes.number.isRequired
};

export default MlRunDuration;
