import { useState } from "react";
import Drawer from "@mui/material/Drawer";
import SideModalHeader from "components/SideModalHeader";
import useStyles from "./SideModal.styles";

const DrawerContent = ({ headerProps, handleClose, children }) => {
  const { showExpand, ...sideModalHeaderProps } = headerProps;

  const [isExpanded, setIsExpanded] = useState(showExpand);

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.sideModal, isExpanded && classes.sideModalExpanded)}>
      <SideModalHeader
        {...sideModalHeaderProps}
        onClose={handleClose}
        isExpanded={isExpanded}
        onExpandChange={() => setIsExpanded(!isExpanded)}
      />
      {children}
    </div>
  );
};

const SideModal = ({ isOpen, closeHandler, dataTestId, headerProps = {}, onClose, children }) => {
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
      <DrawerContent headerProps={headerProps} handleClose={handleClose}>
        {children}
      </DrawerContent>
    </Drawer>
  );
};

export default SideModal;
