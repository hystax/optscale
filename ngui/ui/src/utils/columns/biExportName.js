import React from "react";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import IconLabel from "components/IconLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { getBIExportUrl } from "urls";
import { BI_EXPORT_STATUSES, getBIExportStatus, getBIExportStatusIconSettings } from "utils/biExport";

const biExportName = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_bi_name">
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey: "name",
  style: {
    maxWidth: "400px"
  },
  defaultSort: "asc",
  cell: ({ row: { original } }) => {
    const { id, name, last_status_error: lastStatusError } = original;

    const nameLabel = (
      <Link to={getBIExportUrl(id)} component={RouterLink}>
        {name}
      </Link>
    );

    const status = getBIExportStatus(original);

    if (status === BI_EXPORT_STATUSES.NONE) {
      return nameLabel;
    }

    const { Icon, color, messageId } = getBIExportStatusIconSettings(status);

    return (
      <CaptionedCell caption={status === BI_EXPORT_STATUSES.FAILED ? lastStatusError : undefined}>
        <IconLabel
          icon={
            <Tooltip title={<FormattedMessage id={messageId} />}>
              <Icon fontSize="small" color={color} />
            </Tooltip>
          }
          label={nameLabel}
        />
      </CaptionedCell>
    );
  }
});

export default biExportName;
