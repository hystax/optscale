import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import useStyles from "./FormButtonsWrapper.styles";

const MARGIN = 2;

const FormButtonsWrapper = ({
  children,
  justifyContent = "flex-start",
  alignItems,
  withBottomMargin = false,
  withTopMargin = true
}) => {
  const { classes } = useStyles();
  return (
    <Box
      display="flex"
      mt={withTopMargin ? MARGIN : 0}
      mb={withBottomMargin ? MARGIN : 0}
      justifyContent={justifyContent}
      alignItems={alignItems}
      className={classes.wrapper}
    >
      {children}
    </Box>
  );
};

FormButtonsWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  justifyContent: PropTypes.string,
  alignItems: PropTypes.string,
  withBottomMargin: PropTypes.bool,
  withTopMargin: PropTypes.bool
};

export default FormButtonsWrapper;
