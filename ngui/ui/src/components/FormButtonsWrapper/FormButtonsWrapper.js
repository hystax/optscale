import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import useStyles from "./FormButtonsWrapper.styles";

const FormButtonsWrapper = ({ children, justifyContent = "flex-start", alignItems, mt = 2, mb = 0 }) => {
  const { classes } = useStyles();
  return (
    <Box display="flex" mt={mt} mb={mb} justifyContent={justifyContent} alignItems={alignItems} className={classes.wrapper}>
      {children}
    </Box>
  );
};

FormButtonsWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  justifyContent: PropTypes.string,
  alignItems: PropTypes.string,
  mb: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  mt: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
};

export default FormButtonsWrapper;
