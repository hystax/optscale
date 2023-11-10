import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
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

export default SnackbarAlert;
