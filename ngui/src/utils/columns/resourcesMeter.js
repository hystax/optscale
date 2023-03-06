import React from "react";
import { lighten, useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import { FormattedMessage, FormattedNumber } from "react-intl";
import BufferedProgressBar from "components/BufferedProgressBar";
import CircleLabel from "components/CircleLabel";
import QuestionMark from "components/QuestionMark";
import TextWithDataTestId from "components/TextWithDataTestId";

const MAXIMUM_FRACTION_DIGITS = 2;
const LIMIT_MULTIPLIER = 10;

const Header = ({
  headerDataTestId,
  messageId,
  questionMarkMessageId,
  questionMarkUsedMessageId,
  questionMarkRequestsMessageId,
  questionMarkLimitMessageId,
  questionMarkDataTestId
}) => {
  const theme = useTheme();
  return (
    <Box width="max-content" display="flex" alignItems="center">
      <TextWithDataTestId dataTestId={headerDataTestId}>
        <FormattedMessage id={messageId} />
      </TextWithDataTestId>
      <QuestionMark
        messageId={questionMarkMessageId}
        messageValues={{
          br: <br />,
          strong: (chunks) => <strong>{chunks}</strong>,
          usedCircle: (
            <CircleLabel
              figureColor={theme.palette.primary.main}
              label={
                <FormattedMessage
                  id={questionMarkUsedMessageId}
                  values={{
                    strong: (chunks) => <strong>{chunks}</strong>
                  }}
                />
              }
              textFirst={false}
            />
          ),
          requestsCircle: (
            <CircleLabel
              figureColor={theme.palette.success.light}
              label={
                <FormattedMessage
                  id={questionMarkRequestsMessageId}
                  values={{
                    strong: (chunks) => <strong>{chunks}</strong>
                  }}
                />
              }
              textFirst={false}
            />
          ),
          limitCircle: (
            <CircleLabel
              figureColor={theme.palette.grey.A400}
              label={
                <FormattedMessage
                  id={questionMarkLimitMessageId}
                  values={{
                    strong: (chunks) => <strong>{chunks}</strong>
                  }}
                />
              }
              textFirst={false}
            />
          )
        }}
        dataTestId={questionMarkDataTestId}
      />
    </Box>
  );
};

const Cell = ({
  used,
  requests,
  limit,
  limitExceededMessageId,
  limitNotSetMessageId,
  mismatchedLimitMessageId,
  valueFormatterFn,
  dataTestId
}) => {
  const theme = useTheme();

  let customMessageId = "";
  let valueColor = theme.palette.primary.main;
  let totalColor = theme.palette.grey.A400;

  const divider = limit || requests;
  const percent = (used / divider) * 100;
  const bufferPercent = (requests / divider) * 100;
  if (percent >= bufferPercent) {
    customMessageId = limitExceededMessageId;
    valueColor = theme.palette.secondary.main;
  } else if (divider === 0) {
    customMessageId = limitNotSetMessageId;
    valueColor = theme.palette.secondary.main;
  } else if (limit > used * LIMIT_MULTIPLIER && limit > requests * LIMIT_MULTIPLIER) {
    customMessageId = mismatchedLimitMessageId;
    totalColor = lighten(theme.palette.secondary.main, 0.5);
  }
  const tooltip = {
    show: true,
    valueTooltipMessage: (
      <FormattedMessage
        id="{key}:{value}"
        values={{
          key: <FormattedMessage id={"used"} />,
          value: <strong>{valueFormatterFn(used)}</strong>
        }}
      />
    ),
    valueBufferTooltipMessage: (
      <FormattedMessage
        id="{key}:{value}"
        values={{
          key: <FormattedMessage id={"requests"} />,
          value: requests ? (
            <strong>{valueFormatterFn(requests)}</strong>
          ) : (
            <strong>
              <FormattedMessage id={"none"} />
            </strong>
          )
        }}
      />
    ),
    totalTooltipMessage: (
      <FormattedMessage
        id="{key}:{value}"
        values={{
          key: <FormattedMessage id={"limit"} />,
          value: limit ? (
            <strong>{valueFormatterFn(limit)}</strong>
          ) : (
            <strong>
              <FormattedMessage id={"none"} />
            </strong>
          )
        }}
      />
    ),
    customTooltipMessage: customMessageId ? <FormattedMessage id={customMessageId} /> : ""
  };
  return (
    <BufferedProgressBar
      dataTestId={dataTestId}
      tooltip={tooltip}
      valueColor={valueColor}
      valueBufferColor={theme.palette.success.light}
      totalColor={totalColor}
      value={percent}
      valueBuffer={bufferPercent}
    />
  );
};

const resourcesMeter = ({
  id = "cpu_utilization",
  headerDataTestId = "lbl_cpu_utilization",
  dataTestId = "cpu_utilization",
  messageId = "cpuUtilization",
  questionMarkMessageId = "cpuUtilizationTooltip",
  questionMarkUsedMessageId = "cpuUtilizationTooltip.used",
  questionMarkRequestsMessageId = "cpuUtilizationTooltip.requests",
  questionMarkLimitMessageId = "cpuUtilizationTooltip.limit",
  questionMarkDataTestId = "qmark_cpu_utilization",
  averageUsedAccessor = "average_pod_cpu_used",
  requestsAccessor = "pod_cpu_requests",
  provisionAccessor = "pod_cpu_provision",
  limitExceededMessageId = "cpuUtilizationProgressbarTooltip.limitExceeded",
  limitNotSetMessageId = "cpuUtilizationProgressbarTooltip.limitsNotSet",
  mismatchedLimitMessageId = "cpuUtilizationProgressbarTooltip.mismatchedLimit",
  valueFormatterFn = (value) => <FormattedNumber value={value} maximumFractionDigits={MAXIMUM_FRACTION_DIGITS} />
}) => ({
  id,
  header: (
    <Header
      headerDataTestId={headerDataTestId}
      messageId={messageId}
      questionMarkMessageId={questionMarkMessageId}
      questionMarkUsedMessageId={questionMarkUsedMessageId}
      questionMarkRequestsMessageId={questionMarkRequestsMessageId}
      questionMarkLimitMessageId={questionMarkLimitMessageId}
      questionMarkDataTestId={questionMarkDataTestId}
    />
  ),
  enableGlobalFilter: false,
  enableSorting: false,
  cell: ({ row: { original } }) => (
    <Cell
      used={original[averageUsedAccessor] || 0}
      requests={original[requestsAccessor] || 0}
      limit={original[provisionAccessor] || 0}
      limitExceededMessageId={limitExceededMessageId}
      limitNotSetMessageId={limitNotSetMessageId}
      mismatchedLimitMessageId={mismatchedLimitMessageId}
      valueFormatterFn={valueFormatterFn}
      dataTestId={dataTestId}
    />
  )
});

export default resourcesMeter;
