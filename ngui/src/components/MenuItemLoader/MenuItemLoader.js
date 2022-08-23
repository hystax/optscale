import React, { forwardRef } from "react";
import MuiCircularProgress from "@mui/material/CircularProgress";
import MenuItem from "@mui/material/MenuItem";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { withStyles } from "tss-react/mui";

const SIZE = 22;

const CircularProgress = withStyles(MuiCircularProgress, {
  root: {
    position: "absolute",
    left: `calc(50% - ${SIZE / 2}px)`
  }
});

const MenuItemLoader = forwardRef(({ messageId, text }, ref) => (
  <MenuItem disabled ref={ref}>
    <CircularProgress size={SIZE} />
    {messageId ? <FormattedMessage id={messageId} /> : text}
  </MenuItem>
));

MenuItemLoader.propTypes = {
  messageId: PropTypes.string,
  text: PropTypes.string
};

export default MenuItemLoader;
