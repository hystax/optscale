import React from "react";
import MuiCheckbox from "@mui/material/Checkbox";
import PropTypes from "prop-types";

const Checkbox = ({ cssColor, ...rest }) => {
  const sx = cssColor
    ? {
        color: cssColor,
        "&.Mui-checked": {
          color: cssColor
        }
      }
    : undefined;

  return <MuiCheckbox sx={sx} {...rest} />;
};

Checkbox.propTypes = {
  cssColor: PropTypes.string
};

export default Checkbox;
