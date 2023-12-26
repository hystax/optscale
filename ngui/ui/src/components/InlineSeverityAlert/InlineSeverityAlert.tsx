import { Alert, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import useStyles from "./InlineSeverityAlert.styles";

const InlineSeverityAlert = ({ messageId, messageDataTestId, messageValues, severity = "info", sx = {} }) => {
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
