import React from "react";
import CaptionedCell from "components/CaptionedCell";
import HeaderHelperCell from "components/HeaderHelperCell";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

const DetectedAt = ({ secondTimestamp }) => {
  const timeAgo = useIntervalTimeAgo(secondTimestamp);

  return <CaptionedCell caption={timeAgo}>{format(secondsToMilliseconds(secondTimestamp), EN_FULL_FORMAT)}</CaptionedCell>;
};

const lastUsed = ({ headerDataTestId, accessor = "detected_at" }) => ({
  Header: (
    <HeaderHelperCell
      titleMessageId="detectedAt"
      titleDataTestId={headerDataTestId}
      helperMessageId="recommendationDetectedAtDescription"
    />
  ),
  accessor,
  Cell: ({ cell: { value: secondTimestamp } }) => <DetectedAt secondTimestamp={secondTimestamp} />
});

export default lastUsed;
