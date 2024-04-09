import { FormattedMessage } from "react-intl";
import BINextExportTimeLabel from "components/BINextExportTimeLabel";
import CopyText from "components/CopyText";
import IconStatus from "components/IconStatus";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SummaryList from "components/SummaryList";
import { BI_EXPORT_STATUSES, getBIExportStatusIconSettings } from "utils/biExport";
import { getTimeDistance, unixTimestampToDateTime } from "utils/datetime";

const StatusLabel = ({ status }) => {
  const getValue = () => {
    if (status === BI_EXPORT_STATUSES.NONE) {
      return <FormattedMessage id="none" />;
    }

    const { Icon, color, messageId } = getBIExportStatusIconSettings(status);

    return <IconStatus icon={Icon} color={color} labelMessageId={messageId} />;
  };

  return <KeyValueLabel key="status" keyMessageId="status" value={getValue()} />;
};

const DetailsSummaryList = ({
  id,
  name,
  days,
  createdAt,
  lastRun,
  lastCompleted,
  activity,
  status,
  nextRun,
  lastStatusError,
  isLoading = false
}) => (
  <SummaryList
    titleMessage={<FormattedMessage id="details" />}
    isLoading={isLoading}
    items={[
      <KeyValueLabel
        key="id"
        keyMessageId="id"
        value={
          <CopyText
            text={id}
            sx={{
              fontWeight: "inherit"
            }}
          >
            {id}
          </CopyText>
        }
      />,
      <KeyValueLabel key="name" keyMessageId="name" value={name} />,
      <KeyValueLabel key="exportedDays" keyMessageId="exportedDays" value={days} />,
      <KeyValueLabel key="createdAt" keyMessageId="createdAt" value={unixTimestampToDateTime(createdAt)} />,
      <KeyValueLabel
        key="lastExportAttempt"
        keyMessageId="lastExportAttempt"
        value={
          lastRun === 0 ? (
            <FormattedMessage id="never" />
          ) : (
            <FormattedMessage
              id="valueAgo"
              values={{
                value: getTimeDistance(lastRun)
              }}
            />
          )
        }
      />,
      <KeyValueLabel
        key="lastSuccessfulExport"
        keyMessageId="lastSuccessfulExport"
        value={
          lastCompleted === 0 ? (
            <FormattedMessage id="never" />
          ) : (
            <FormattedMessage
              id="valueAgo"
              values={{
                value: getTimeDistance(lastCompleted)
              }}
            />
          )
        }
      />,
      <KeyValueLabel
        key="nextExport"
        keyMessageId="nextExport"
        value={<BINextExportTimeLabel nextRun={nextRun} activity={activity} />}
      />,
      <StatusLabel key="status" status={status} />,
      lastStatusError ? (
        <KeyValueLabel
          key="reason"
          keyMessageId="reason"
          value={lastStatusError}
          sx={{
            maxWidth: "600px"
          }}
        />
      ) : undefined,
      <KeyValueLabel key="activity" keyMessageId="activity" value={<FormattedMessage id={activity} />} />
    ].filter(Boolean)}
  />
);

export default DetailsSummaryList;
