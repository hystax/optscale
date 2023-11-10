import { useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import Typography from "@mui/material/Typography";
import Button from "components/Button";
import SubTitle from "components/SubTitle";

import useStyles from "./AlertDialog.styles";

const AlertDialog = ({ show, header, message, buttonMessageId, onClose, dataTestIds = {} }) => {
  const [open, setOpen] = useState(show);

  const buttonClickHandler = () => {
    setOpen(false);
    if (typeof onClose === "function") onClose();
  };

  const { classes } = useStyles();

  const { paper: paperDataTestId, title: titleMessageDataTestId, button: buttonDataTestId } = dataTestIds;

  return (
    <Dialog
      PaperProps={{ "data-test-id": paperDataTestId }}
      open={open}
      aria-describedby="alert-dialog-description"
      maxWidth="md"
    >
      {header && (
        <SubTitle
          className={classes.alertDialogHeader}
          align="center"
          id="responsive-dialog-title"
          dataTestId={titleMessageDataTestId}
        >
          {header}
        </SubTitle>
      )}
      <DialogContent id="alert-dialog-description" color="inherit">
        <Typography className={classes.alertDialogText} component="span">
          {message}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button
          messageId={buttonMessageId}
          onClick={buttonClickHandler}
          variant="contained"
          color="primary"
          dataTestId={buttonDataTestId}
        />
      </DialogActions>
    </Dialog>
  );
};

export default AlertDialog;
