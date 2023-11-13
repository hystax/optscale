import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatDuration } from "hooks/useFormatDuration";
import { secondsToMilliseconds } from "utils/datetime";

const Duration = ({ rawDuration, rawDurationThreshold }) => {
  const duration = useFormatDuration(secondsToMilliseconds(rawDuration));
  const durationThreshold = useFormatDuration(secondsToMilliseconds(rawDurationThreshold));

  return (
    <FormattedMessage
      id="{value}OutOf{defaultValue}"
      values={{
        value: duration,
        defaultValue: durationThreshold
      }}
    />
  );
};

const mlLocalStorageBottleneckDuration = ({ headerDataTestId = "lbl_duration" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="duration" />
    </TextWithDataTestId>
  ),
  id: "duration",
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({ row: { original } }) => (
    <Duration rawDuration={original.duration} rawDurationThreshold={original.duration_threshold} />
  )
});

export default mlLocalStorageBottleneckDuration;
