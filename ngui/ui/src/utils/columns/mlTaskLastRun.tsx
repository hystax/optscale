import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import MlRunStatus from "components/MlRunStatus";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";

const LastRunStatus = ({ lastRun, status }) => {
  const timeAgo = useIntervalTimeAgo(lastRun, 1);
  return (
    <CaptionedCell caption={[{ node: timeAgo, key: "time" }]}>
      <MlRunStatus status={status} />
    </CaptionedCell>
  );
};

const mlTaskLastRun = ({ id = "last_run", columnSelector } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_last_run">
      <FormattedMessage id="lastRun" />
    </TextWithDataTestId>
  ),
  id,
  columnSelector,
  cell: ({ row: { original } }) =>
    original.last_run === 0 ? (
      <FormattedMessage id="never" />
    ) : (
      <LastRunStatus lastRun={original.last_run} status={original.status} />
    )
});

export default mlTaskLastRun;
