import { Typography, useTheme } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SettingsLink from "components/common/SettingsLink";
import { addDays, EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { LimitExceededAlertProps } from "../types";
import StatusAlert from "./StatusAlert";

const ALERT_COLOR = "error";

const LimitExceededAlert = ({ gracePeriodStart, gracePeriodDays }: LimitExceededAlertProps) => {
  const theme = useTheme();
  const disabledAt = format(addDays(secondsToMilliseconds(gracePeriodStart), gracePeriodDays), EN_FULL_FORMAT);

  return (
    <StatusAlert color={ALERT_COLOR}>
      <Typography gutterBottom align="center">
        <FormattedMessage
          id="organizationUsageLimitExceeded"
          values={{
            manageSettingsLabel: (chunks) => (
              <SettingsLink color={theme.palette[ALERT_COLOR].contrastText} underline="always" tab="subscription">
                {chunks}
              </SettingsLink>
            ),
          }}
        />
      </Typography>
      <Typography align="center">
        <FormattedMessage
          id="organizationWillBeDisabledStartingOn"
          values={{ time: disabledAt, strong: (chunks) => <strong>{chunks}</strong> }}
        />
      </Typography>
    </StatusAlert>
  );
};

export default LimitExceededAlert;
