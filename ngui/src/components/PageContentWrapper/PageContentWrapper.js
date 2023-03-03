import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import useStyles from "./PageContentWrapper.styles";

const PageContentWrapper = ({ children }) => {
  const { classes } = useStyles();

  return <Box className={classes.page}>{children}</Box>;
};

PageContentWrapper.propTypes = {
  children: PropTypes.node
};

export default PageContentWrapper;
