import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { format } from "date-fns";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import IconStatus from "components/IconStatus";
import TextWithDataTestId from "components/TextWithDataTestId";
import { EN_FULL_FORMAT, secondsToMilliseconds } from "utils/datetime";
import { CELL_EMPTY_VALUE } from "utils/tables";

export const DISCOVERY_STATUS = Object.freeze({
  UNKNOWN: 0,
  ERROR: 1,
  SUCCESS: 2
});

const ErrorStatus = ({ errorAt, errorText }) => (
  <CaptionedCell
    caption={[
      { node: format(secondsToMilliseconds(errorAt), EN_FULL_FORMAT), key: "error-at" },
      { node: errorText, key: "error-text" }
    ]}
  >
    <IconStatus icon={CancelIcon} color="error" labelMessageId="failed" />
  </CaptionedCell>
);

const UnknownStatus = () => CELL_EMPTY_VALUE;

const discoveryStatus = ({ headerDataTestId = "lbl_status", messageId = "status", accessorKey = "status" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={messageId} />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell, row: { original } }) => {
    const status = cell.getValue();

    if (status === DISCOVERY_STATUS.ERROR) {
      return <ErrorStatus errorAt={original.last_error_at} errorText={original.last_error} />;
    }

    if (status === DISCOVERY_STATUS.SUCCESS) {
      return <IconStatus icon={CheckCircleIcon} color="success" labelMessageId="completed" />;
    }

    return <UnknownStatus />;
  }
});

export default discoveryStatus;
