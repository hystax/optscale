import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

type DurationProps = {
  duration: {
    weeks: number;
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
    milliseconds: number;
  };
};

const Duration = ({ duration }: DurationProps) => {
  const formatInterval = useFormatIntervalDuration();

  return (
    <KeyValueLabel
      keyMessageId="duration"
      value={formatInterval({
        formatTo: [
          INTERVAL_DURATION_VALUE_TYPES.WEEKS,
          INTERVAL_DURATION_VALUE_TYPES.DAYS,
          INTERVAL_DURATION_VALUE_TYPES.HOURS,
          INTERVAL_DURATION_VALUE_TYPES.MINUTES,
        ],
        duration,
      })}
    />
  );
};

export default Duration;
