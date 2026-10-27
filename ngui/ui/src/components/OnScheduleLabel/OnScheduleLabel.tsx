import ScheduleOutlinedIcon from "@mui/icons-material/ScheduleOutlined";
import { Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, matchPath, useLocation } from "react-router-dom";
import IconLabel from "components/IconLabel";
import { POWER_SCHEDULE_DETAILS, getPowerScheduleDetailsUrl } from "urls";

type PowerScheduleId = string;

type OnScheduleLabelProps = {
  powerScheduleId: PowerScheduleId;
  display?: string;
};

const useShowLink = (powerScheduleId: PowerScheduleId) => {
  const location = useLocation();

  const powerSchedulePath = matchPath(POWER_SCHEDULE_DETAILS, location.pathname);

  if (powerSchedulePath) {
    const {
      params: { powerScheduleId: routePowerScheduleId },
    } = powerSchedulePath;

    if (routePowerScheduleId === powerScheduleId) {
      return false;
    }
  }
  return true;
};

const OnScheduleLabel = ({ powerScheduleId, display = "inline-flex" }: OnScheduleLabelProps) => {
  const showLink = useShowLink(powerScheduleId);

  return (
    <IconLabel
      icon={<ScheduleOutlinedIcon fontSize="inherit" color="success" />}
      display={display}
      label={
        showLink ? (
          <Link
            to={getPowerScheduleDetailsUrl(powerScheduleId)}
            component={RouterLink}
            variant="caption"
            sx={{ fontWeight: "normal", whiteSpace: "nowrap" }}
          >
            <FormattedMessage id="onSchedule" />
          </Link>
        ) : (
          <Typography variant="caption" noWrap>
            <FormattedMessage id="onSchedule" />
          </Typography>
        )
      }
    />
  );
};

export default OnScheduleLabel;
