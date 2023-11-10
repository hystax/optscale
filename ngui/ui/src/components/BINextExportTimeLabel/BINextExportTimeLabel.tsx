import { FormattedMessage } from "react-intl";
import { BI_EXPORT_ACTIVITY_STATUSES } from "utils/biExport";
import { getCurrentUTCTimeInSec, getTimeDistance } from "utils/datetime";

const BINextExportTimeLabel = ({ nextRun, activity }) => {
  if (nextRun <= getCurrentUTCTimeInSec()) {
    return <FormattedMessage id="aboutToStart" />;
  }

  if (activity === BI_EXPORT_ACTIVITY_STATUSES.RUNNING) {
    return <FormattedMessage id="running" />;
  }

  return (
    <FormattedMessage
      id="valueIn"
      values={{
        value: getTimeDistance(nextRun)
      }}
    />
  );
};

export default BINextExportTimeLabel;
