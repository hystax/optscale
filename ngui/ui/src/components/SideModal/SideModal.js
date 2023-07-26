import React, { useState, useEffect } from "react";
import Drawer from "@mui/material/Drawer";
import PropTypes from "prop-types";
import SideModalHeader from "components/SideModalHeader";
import useStyles from "./SideModal.styles";

const SideModal = ({ isOpen, closeHandler, dataTestId, headerProps = {}, onClose, children }) => {
  const { classes, cx } = useStyles();

  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    setIsExpanded(headerProps.showExpand);
  }, [headerProps.showExpand]);

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
      SlideProps={{
        "data-test-id": dataTestId
      }}
      anchor="right"
      open={isOpen}
      onClose={handleClose}
      style={{ wordBreak: "break-word" }}
    >
      <div className={cx(classes.sideModal, isExpanded && classes.sideModalExpanded)}>
        <SideModalHeader
          {...headerProps}
          onClose={handleClose}
          isExpanded={isExpanded}
          onExpandChange={() => setIsExpanded(!isExpanded)}
        />
        {children}
      </div>
    </Drawer>
  );
};

SideModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  headerProps: PropTypes.exact({
    showExpand: PropTypes.bool,
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
