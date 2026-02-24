import { Alert, Typography, type AlertProps, type SxProps, type Theme } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { IntlFormatValues } from "utils/types";
import useStyles from "./InlineSeverityAlert.styles";

type TextOrMessageIdProps =
  | { text: string; messageId?: never; messageValues?: never; messageDataTestId?: never }
  | { text?: never; messageId: string; messageValues?: IntlFormatValues; messageDataTestId?: string };

export type InlineSeverityAlertProps = TextOrMessageIdProps & {
  severity?: AlertProps["severity"];
  sx?: SxProps<Theme>;
};

const InlineSeverityAlert = ({
  text,
  messageId,
  messageValues,
  messageDataTestId,
  severity = "info",
  sx = {},
}: InlineSeverityAlertProps) => {
  const { classes } = useStyles();

  const content = text ?? <FormattedMessage id={messageId} values={messageValues} />;

  return (
    <Alert severity={severity} className={classes.alert} sx={sx}>
      <Typography data-test-id={messageDataTestId} component="div">
        {content}
      </Typography>
    </Alert>
  );
};

export default InlineSeverityAlert;
