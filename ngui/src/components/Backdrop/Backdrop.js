import React from "react";
import MuiBackdrop from "@mui/material/Backdrop";
import Collapse from "@mui/material/Collapse";
import PropTypes from "prop-types";
import useStyles from "./Backdrop.styles";

const Backdrop = ({ children, customClass, open = true, aboveDrawers = false }) => {
  const { classes, cx } = useStyles(aboveDrawers);

  return (
    <MuiBackdrop className={cx(classes.backdrop, classes[customClass])} open={open} TransitionComponent={Collapse}>
      {children}
    </MuiBackdrop>
  );
};

Backdrop.propTypes = {
  children: PropTypes.node,
  customClass: PropTypes.string,
  open: PropTypes.bool,
  aboveDrawers: PropTypes.bool
};

export default Backdrop;
