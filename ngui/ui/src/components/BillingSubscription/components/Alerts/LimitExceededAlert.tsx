import { Alert, Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { addDays, EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

type LimitExceededAlertProps = {
  gracePeriodStart: number;
  gracePeriodDays: number;
};

const LimitExceededAlert = ({ gracePeriodStart, gracePeriodDays }: LimitExceededAlertProps) => {
  const disabledAt = format(addDays(secondsToMilliseconds(gracePeriodStart), gracePeriodDays), EN_FULL_FORMAT);
  return (
    <Alert severity="error">
      <Box mb={1}>
        <FormattedMessage
          id="organizationUsageLimitExceeded"
          values={{
            manageSettingsLabel: (chunks) => chunks,
          }}
        />
      </Box>
      <Box>
        <FormattedMessage
          id="organizationWillBeDisabledStartingOn"
          values={{ time: disabledAt, strong: (chunks) => <strong>{chunks}</strong> }}
        />
      </Box>
    </Alert>
  );
};

export default LimitExceededAlert;
