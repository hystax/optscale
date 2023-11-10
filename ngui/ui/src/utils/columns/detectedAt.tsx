import CaptionedCell from "components/CaptionedCell";
import HeaderHelperCell from "components/HeaderHelperCell";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const DetectedAt = ({ secondTimestamp }) => {
  const timeAgo = useIntervalTimeAgo(secondTimestamp);

  return <CaptionedCell caption={timeAgo}>{format(secondsToMilliseconds(secondTimestamp), EN_FULL_FORMAT)}</CaptionedCell>;
};

const detectedAt = ({ headerDataTestId, accessor = "detected_at" }) => ({
  header: (
    <HeaderHelperCell
      titleMessageId="detectedAt"
      titleDataTestId={headerDataTestId}
      helperMessageId="recommendationDetectedAtDescription"
    />
  ),
  accessorKey: accessor,
  cell: ({ cell }) => <DetectedAt secondTimestamp={cell.getValue()} />
});

export default detectedAt;
