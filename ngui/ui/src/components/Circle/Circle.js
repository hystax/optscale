import React, { forwardRef } from "react";
import CircleIcon from "@mui/icons-material/Circle";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";

const Circle = forwardRef((props, ref) => {
  const { mr = 0, ml = 0, color = "inherit", ...rest } = props;

  const theme = useTheme();

  const circleColor = theme.palette[color] ? theme.palette[color].light : color;

  return (
    <CircleIcon
      ref={ref}
      sx={{
        marginRight: theme.spacing(mr),
        marginLeft: theme.spacing(ml),
        color: circleColor
      }}
      fontSize="inherit"
      {...rest}
    />
  );
});

Circle.propTypes = {
  color: PropTypes.string,
  mr: PropTypes.number,
  ml: PropTypes.number
};

export default Circle;
