import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import { Typography, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import IconLabel from "components/IconLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { getPowerScheduleDetailsUrl } from "urls";

const powerScheduleName = ({
  id,
  accessorFn,
  accessorKey,
  headerDataTestId,
  headerMessageId,
  cellDataAccessors: { enabled: enabledAccessor, id: idAccessor } = {}
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
    const name = cell.getValue();
    const { [enabledAccessor]: enabled, [idAccessor]: powerScheduleId } = original;
    return (
      <IconLabel
        icon={
          <Tooltip title={<FormattedMessage id={enabled ? "active" : "inactive"} />}>
            {enabled ? (
              <PlayCircleOutlineOutlinedIcon fontSize="small" color="success" />
            ) : (
              <StopCircleOutlinedIcon fontSize="small" color="error" />
            )}
          </Tooltip>
        }
        label={
          <Typography noWrap>
            <Link to={getPowerScheduleDetailsUrl(powerScheduleId)} component={RouterLink}>
              {name}
            </Link>
          </Typography>
        }
      />
    );
  }
});

export default powerScheduleName;
