import CaptionedCell from "components/CaptionedCell";
import HeaderHelperCell from "components/HeaderHelperCell";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

type CellRowData = { cell: { getValue: () => number } };

type DetectedAtConfig = {
  headerDataTestId?: string;
  accessor?: string;
};

type DetectedAtProps = {
  secondTimestamp: number;
};

const DetectedAt = ({ secondTimestamp }: DetectedAtProps) => {
  const timeAgo = useIntervalTimeAgo(secondTimestamp);

  return <CaptionedCell caption={timeAgo}>{format(secondsToMilliseconds(secondTimestamp), EN_FULL_FORMAT)}</CaptionedCell>;
};

const detectedAt = ({ headerDataTestId, accessor = "detected_at" }: DetectedAtConfig = {}) => ({
  header: (
    <HeaderHelperCell
      titleMessageId="detectedAt"
      titleDataTestId={headerDataTestId}
      helperMessageId="recommendationDetectedAtDescription"
    />
  ),
  accessorKey: accessor,
  cell: ({ cell }: CellRowData) => <DetectedAt secondTimestamp={cell.getValue()} />,
});

export default detectedAt;
