import { Alert, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import useStyles from "./InlineSeverityAlert.styles";

const InlineSeverityAlert = ({ messageId, messageDataTestId, messageValues, sx = {} }) => {
  const { classes } = useStyles();

  return (
    <Alert severity="info" className={classes.alert} sx={sx}>
      <Typography data-test-id={messageDataTestId}>
        <FormattedMessage id={messageId} values={messageValues} />
      </Typography>
    </Alert>
  );
};

export default InlineSeverityAlert;
