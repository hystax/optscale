import React, { useState } from "react";
import MuiPopover from "@mui/material/Popover";
import PropTypes from "prop-types";
import Button from "components/Button";
import { isEmpty } from "utils/arrays";
import useStyles from "./Popover.styles";

const Popover = ({
  anchorOrigin,
  transformOrigin,
  buttons = [],
  handleClose,
  label,
  menu,
  dataTestIds = {},
  rightLabelPosition = false
}) => {
  const { classes } = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget.children[0]);
  };

  const { label: labelDataTestId, popover: popOverDataTestId } = dataTestIds;

  const onClose = () => {
    if (typeof handleClose === "function") {
      handleClose();
    }
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;

  const renderButtons = () => (
    <div className={classes.buttonsWrapper}>
      {buttons.map(({ messageId, variant = "text", color = "primary", onClick, closable, dataTestId }) => (
        <Button
          key={messageId}
          variant={variant}
          messageId={messageId}
          color={color}
          onClick={() => {
            if (typeof onClick === "function") {
              onClick();
            }
            if (closable) {
              onClose();
            }
          }}
          dataTestId={dataTestId}
        />
      ))}
    </div>
  );

  return (
    <div className={classes.container}>
      <div
        aria-describedby={id}
        variant="contained"
        onClick={handleClick}
        data-test-id={labelDataTestId}
        className={rightLabelPosition ? classes.rightLabelPosition : ""}
        style={{ height: "100%" }}
      >
        {typeof label === "function" ? label({ isOpen: open }) : label}
      </div>
      <MuiPopover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={onClose}
        anchorOrigin={
          anchorOrigin || {
            vertical: "bottom",
            horizontal: "right"
          }
        }
        transformOrigin={
          transformOrigin || {
            vertical: "top",
            horizontal: "right"
          }
        }
        PaperProps={{ "data-test-id": popOverDataTestId }}
      >
        {menu}
        {!isEmpty(buttons) && renderButtons()}
      </MuiPopover>
    </div>
  );
};

Popover.propTypes = {
  label: PropTypes.oneOfType([PropTypes.node, PropTypes.func]).isRequired,
  menu: PropTypes.node.isRequired,
  anchorOrigin: PropTypes.object,
  handleClose: PropTypes.func,
  transformOrigin: PropTypes.object,
  buttons: PropTypes.array,
  dataTestIds: PropTypes.shape({
    label: PropTypes.string
  }),
  rightLabelPosition: PropTypes.bool
};

export default Popover;
