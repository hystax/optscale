import React, { useEffect } from "react";
import CloseIcon from "@mui/icons-material/Close";
import Alert from "@mui/material/Alert";
import PropTypes from "prop-types";
import IconButton from "components/IconButton";
import useStyles from "./TopAlert.styles";

const TopAlert = ({ alert }) => {
  const { classes, cx } = useStyles();

  useEffect(() => {
    if (!alert.triggered && typeof alert.onTrigger === "function") {
      alert.onTrigger();
    }
  }, [alert]);

  const alertType = alert.type ?? "secondary";

  return (
    <Alert
      action={
        <IconButton
          customClass="close-alert-button"
          dataTestId="btn_close_top_alert"
          onClick={() => {
            if (typeof alert.onClose === "function") {
              alert.onClose();
            }
          }}
          icon={<CloseIcon />}
        />
      }
      data-test-id={alert.dataTestId}
      icon={false}
      className={cx(classes.alert, classes[alertType])}
    >
      <span data-test-id="title_top_alert">{alert.getContent()}</span>
    </Alert>
  );
};

TopAlert.propTypes = {
  alert: PropTypes.shape({
    onClose: PropTypes.func,
    triggered: PropTypes.bool,
    onTrigger: PropTypes.func,
    type: PropTypes.oneOf(["secondary", "success", "info"]),
    getContent: PropTypes.func,
    dataTestId: PropTypes.string
  })
};

export default TopAlert;
