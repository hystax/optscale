import React from "react";
import Drawer from "@mui/material/Drawer";
import PropTypes from "prop-types";
import SideModalHeader from "components/SideModalHeader";
import useStyles from "./SideModal.styles";

const SideModal = ({ isOpen, closeHandler, dataTestId, headerProps = {}, onClose, children }) => {
  const { classes } = useStyles();

  const handleClose = (event) => {
    if (event.type === "keydown" && (event.key === "Tab" || event.key === "Shift")) {
      return;
    }
    if (typeof closeHandler === "function") {
      closeHandler(false);
    }
    if (typeof onClose === "function") {
      onClose(event);
    }
  };

  return (
    <Drawer
      classes={{
        paper: classes.sideModal
      }}
      SlideProps={{
        "data-test-id": dataTestId
      }}
      anchor="right"
      open={isOpen}
      onClose={handleClose}
      style={{ wordBreak: "break-word" }}
    >
      <SideModalHeader {...headerProps} onClose={handleClose} />
      {children}
    </Drawer>
  );
};

SideModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  headerProps: PropTypes.exact({
    messageId: PropTypes.string.isRequired,
    formattedMessageValues: PropTypes.object,
    dataTestIds: PropTypes.object,
    color: PropTypes.string
  }).isRequired,
  dataTestId: PropTypes.string,
  children: PropTypes.node,
  closeHandler: PropTypes.func,
  onClose: PropTypes.func
};

export default SideModal;
