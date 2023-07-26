import React from "react";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import QuestionMark from "components/QuestionMark";
import TextWithDataTestId from "components/TextWithDataTestId";
import { intl } from "translations/react-intl-config";
import ApproximatelyZero from "../../components/ApproximatelyZero";

const MAXIMUM_FRACTION_DIGITS = 2;
const APPROXIMATE_ZERO_THRESHOLD = 0.01;

const resourcesUsed = ({
  headerDataTestId = "lbl_total_pod_memory_gb",
  dataTestId = "total_pod_memory_gb",
  messageId = "memoryHours",
  questionMarkMessageId = "totalPodMemoryUsedTooltip",
  accessorKey = "recommended_flavor",
  totalAccessor = "total_pod_memory_gb",
  totalRequestsAccessor = "total_pod_memory_requests_gb"
}) => ({
  header: (
    <Box display="flex" alignItems="center">
      <TextWithDataTestId dataTestId={headerDataTestId}>
        <FormattedMessage id={messageId} />
      </TextWithDataTestId>
      <QuestionMark
        messageId={questionMarkMessageId}
        messageValues={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    </Box>
  ),
  accessorKey,
  enableSorting: false,
  enableGlobalFilter: false,
  cell: ({ row: { original } }) => {
    let value1;
    let value2;
    if (original[totalAccessor] < APPROXIMATE_ZERO_THRESHOLD) {
      value1 = <ApproximatelyZero />;
    } else {
      value1 = intl.formatNumber(original[totalAccessor], { maximumFractionDigits: MAXIMUM_FRACTION_DIGITS });
    }
    if (!original[totalRequestsAccessor]) {
      value2 = "-";
    } else if (original[totalRequestsAccessor] < APPROXIMATE_ZERO_THRESHOLD) {
      value2 = <ApproximatelyZero />;
    } else {
      value2 = intl.formatNumber(original[totalRequestsAccessor], { maximumFractionDigits: MAXIMUM_FRACTION_DIGITS });
    }
    return (
      <TextWithDataTestId dataTestId={dataTestId}>
        <FormattedMessage
          id="value / value"
          values={{
            value1,
            value2
          }}
        />
      </TextWithDataTestId>
    );
  },
  style: {
    maxWidth: 130
  }
});

export default resourcesUsed;
