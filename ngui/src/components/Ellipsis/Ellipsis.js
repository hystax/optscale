import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import useStyles from "./Ellipsis.styles";

const Ellipsis = ({ variant, component = "span", className = "" }) => {
  const { classes } = useStyles();
  return (
    <Typography className={classes[className]} component={component} variant={variant}>
      ...
    </Typography>
  );
};

Ellipsis.propTypes = {
  variant: PropTypes.string,
  component: PropTypes.string,
  className: PropTypes.string
};

export default Ellipsis;
