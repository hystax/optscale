import { ReactNode, SyntheticEvent, useState } from "react";
import Drawer from "@mui/material/Drawer";
import SideModalHeader from "components/SideModalHeader";
import { SideModalHeaderProps } from "components/SideModalHeader/SideModalHeader";
import useStyles from "./SideModal.styles";

type DrawerContentProps = {
  headerProps: SideModalHeaderProps;
  handleClose: (event: SyntheticEvent) => void;
  children: ReactNode;
};

type SideModalProps = {
  isOpen: boolean;
  closeHandler: (isOpen: boolean) => void;
  dataTestId: string;
  headerProps: SideModalHeaderProps;
  onClose?: (event: SyntheticEvent) => void;
  children: ReactNode;
};

const DrawerContent = ({ headerProps, handleClose, children }: DrawerContentProps) => {
  const { showExpand, ...sideModalHeaderProps } = headerProps;

  const [isExpanded, setIsExpanded] = useState(showExpand);

  const { classes, cx } = useStyles();

  return (
    <div className={cx(classes.sideModal, isExpanded && classes.sideModalExpanded)}>
      <SideModalHeader
        {...sideModalHeaderProps}
        showExpand={showExpand}
        onClose={handleClose}
        isExpanded={isExpanded}
        onExpandChange={() => setIsExpanded(!isExpanded)}
      />
      {children}
    </div>
  );
};

const SideModal = ({ isOpen, closeHandler, dataTestId, headerProps, onClose, children }: SideModalProps) => {
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
