import CancelIcon from "@mui/icons-material/Cancel";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import IconLabel from "components/IconLabel";
import IntervalTimeAgo from "components/IntervalTimeAgo";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { intl } from "translations/react-intl-config";
import { formatIntervalTimeAgo } from "utils/datetime";

const powerScheduleLastRun = ({
  id,
  accessorFn,
  accessorKey,
  headerDataTestId,
  headerMessageId,
  cellDataAccessors: { lastRunError: lastRunErrorAccessor } = {}
}) => ({
  id,
  accessorFn,
  accessorKey,
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  ),
  cell: ({ cell, row: { original } }) => {
    const lastRunTime = cell.getValue();
    const { [lastRunErrorAccessor]: lastRunError } = original;

    return (
      <CaptionedCell
        caption={
          lastRunError
            ? {
                key: "error",
                node: (
                  <Typography component="div" variant="caption">
                    <Tooltip title={lastRunError}>
                      <span>
                        <IconLabel
                          icon={<CancelIcon fontSize="inherit" color="error" />}
                          label={<FormattedMessage id="failed" />}
                        />
                      </span>
                    </Tooltip>
                  </Typography>
                )
              }
            : undefined
        }
      >
        {lastRunTime === 0 ? <FormattedMessage id="never" /> : <IntervalTimeAgo secondsTimestamp={lastRunTime} precision={1} />}
      </CaptionedCell>
    );
  },
  globalFilterFn: (cellValue, filterValue) => {
    const search = filterValue.toLocaleLowerCase();
    const formattedCellValue =
      cellValue === 0
        ? intl.formatMessage({ id: "never" })
        : formatIntervalTimeAgo({
            agoSecondsTimestamp: cellValue,
            precision: 1,
            intlFormatter: intl
          });

    return formattedCellValue.toLocaleLowerCase().includes(search);
  }
});

export default powerScheduleLastRun;
