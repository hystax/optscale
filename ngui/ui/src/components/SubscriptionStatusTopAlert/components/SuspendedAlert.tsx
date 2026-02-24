import { Typography, useTheme } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SettingsLink from "components/common/SettingsLink";
import StatusAlert from "./StatusAlert";

const ALERT_COLOR = "error";

const SuspendedAlert = () => {
  const theme = useTheme();

  return (
    <StatusAlert color={ALERT_COLOR}>
      <Typography gutterBottom align="center">
        <FormattedMessage id="organizationSubscriptionSuspended" />
      </Typography>
      <Typography align="center">
        <FormattedMessage
          id="organizationSubscriptionSuspendedReactivate"
          values={{
            subscriptionSettingsLabel: (chunks) => (
              <SettingsLink color={theme.palette[ALERT_COLOR].contrastText} underline="always" tab="subscription">
                {chunks}
              </SettingsLink>
            ),
          }}
        />
      </Typography>
    </StatusAlert>
  );
};

export default SuspendedAlert;
