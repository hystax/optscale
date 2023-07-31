import React from "react";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import PropTypes from "prop-types";
import useStyles from "./SnackbarAlert.styles";

const SnackbarAlert = ({ body, openState, handleClose, severity = "info", dataTestIds = {}, autoHideDuration = 10000 }) => {
  const { classes } = useStyles();

  const { snackbar: snackbarDataTestId } = dataTestIds;

  return (
    <div className={classes.root}>
      <Snackbar
        data-test-id={snackbarDataTestId}
        open={openState}
        autoHideDuration={autoHideDuration}
        onClose={handleClose}
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <Alert onClose={handleClose} severity={severity} elevation={6} variant="filled">
          {body}
        </Alert>
      </Snackbar>
    </div>
  );
};

SnackbarAlert.propTypes = {
  openState: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  body: PropTypes.node,
  severity: PropTypes.string,
  dataTestIds: PropTypes.shape({
    snackbar: PropTypes.string
  }),
  autoHideDuration: PropTypes.number
};

export default SnackbarAlert;
