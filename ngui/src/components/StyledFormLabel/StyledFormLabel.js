import React from "react";
import FormLabel from "@mui/material/FormLabel";
import PropTypes from "prop-types";
import useStyles from "./StyledFormLabel.styles";

const StyledFormLabel = ({ children, ...rest }) => {
  const { classes } = useStyles();
  return (
    <FormLabel {...rest} className={classes.label}>
      {children}
    </FormLabel>
  );
};

StyledFormLabel.propTypes = {
  children: PropTypes.node.isRequired,
  labelProps: PropTypes.object
};

export default StyledFormLabel;
