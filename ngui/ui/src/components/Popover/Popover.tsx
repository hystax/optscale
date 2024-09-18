import { useState } from "react";
import MuiPopover from "@mui/material/Popover";
import Button from "components/Button";
import { isEmpty } from "utils/arrays";
import useStyles from "./Popover.styles";

const Popover = ({
  anchorOrigin,
  transformOrigin,
  buttons: buttonsProperty = [],
  handleClose,
  label,
  menu,
  renderMenu,
  dataTestIds = {},
  rightLabelPosition = false,
  disabled = false,
  fullWidth
}) => {
  const { cx, classes } = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);
  const handleClick = (event) => {
    if (disabled) {
      return;
    }
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

  const renderButtons = (buttons) => (
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
    <div className={cx(classes.container, fullWidth && classes.fullWidth)}>
      <div
        aria-describedby={id}
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
        {typeof renderMenu === "function" ? (
          renderMenu({ closeHandler: onClose })
        ) : (
          <>
            {menu}
            {!isEmpty(buttonsProperty) && renderButtons(buttonsProperty)}
          </>
        )}
      </MuiPopover>
    </div>
  );
};

export default Popover;
