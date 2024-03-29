import { ReactNode } from "react";
import { Alert, AlertProps, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import useStyles from "./InlineSeverityAlert.styles";

type InlineSeverityAlertProps = {
  messageId: string;
  messageValues?: Record<string, ReactNode>;
  messageDataTestId?: string;
  severity?: AlertProps["severity"];
  sx?: Record<string, unknown>;
};

const InlineSeverityAlert = ({
  messageId,
  messageValues,
  messageDataTestId,
  severity = "info",
  sx = {}
}: InlineSeverityAlertProps) => {
  const { classes } = useStyles();

  return (
    <Alert severity={severity} className={classes.alert} sx={sx}>
      <Typography data-test-id={messageDataTestId}>
        <FormattedMessage id={messageId} values={messageValues} />
      </Typography>
    </Alert>
  );
};

export default InlineSeverityAlert;
