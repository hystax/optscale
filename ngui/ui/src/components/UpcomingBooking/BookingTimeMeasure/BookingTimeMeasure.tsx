import KeyValueLabel from "components/KeyValueLabel";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { INFINITY_SIGN } from "utils/constants";
import { INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

const BookingTimeMeasure = ({ messageId, measure }) => {
  const formatInterval = useFormatIntervalDuration();

  return (
    <KeyValueLabel
      noWrap
      messageId={messageId}
      value={
        measure === INFINITY_SIGN
          ? INFINITY_SIGN
          : formatInterval({
              formatTo: [
                INTERVAL_DURATION_VALUE_TYPES.WEEKS,
                INTERVAL_DURATION_VALUE_TYPES.DAYS,
                INTERVAL_DURATION_VALUE_TYPES.HOURS,
                INTERVAL_DURATION_VALUE_TYPES.MINUTES
              ],
              duration: measure
            })
      }
    />
  );
};

export default BookingTimeMeasure;
