import { useState } from "react";
import MuiPopover from "@mui/material/Popover";

const Popover = ({ children, popoverContent, popoverId, onClose }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (e) => {
    setAnchorEl(e.currentTarget);
  };

  const handleClose = () => {
    if (typeof onClose === "function") {
      onClose();
    }
    setAnchorEl(null);
  };

  const isPopoverOpen = Boolean(anchorEl);
  const id = isPopoverOpen ? popoverId : undefined;

  return (
    <>
      <div aria-describedby={id} onClick={handleClick} style={{ height: "100%" }}>
        {children}
      </div>
      <MuiPopover
        id={id}
        open={isPopoverOpen}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center"
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "center"
        }}
      >
        {popoverContent}
      </MuiPopover>
    </>
  );
};

export default Popover;
