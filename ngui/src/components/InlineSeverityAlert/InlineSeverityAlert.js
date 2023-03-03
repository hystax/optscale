import React from "react";
import { Alert, Typography } from "@mui/material";
import PropTypes from "prop-types";
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

InlineSeverityAlert.propTypes = {
  messageId: PropTypes.string.isRequired,
  messageValues: PropTypes.object,
  messageDataTestId: PropTypes.string,
  sx: PropTypes.object
};

export default InlineSeverityAlert;
