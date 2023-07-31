import React from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import PropTypes from "prop-types";
import Backdrop from "components/Backdrop";
import useStyles from "./ContentBackdrop.styles";

const ContentBackdrop = ({ children, bannerContent, bannerMaxWidth, icon }) => {
  const { classes } = useStyles({
    bannerMaxWidth
  });

  return (
    <>
      <Paper data-test-id="banner_mockup" variant="elevation" elevation={3} className={classes.root}>
        {icon && <icon.Component data-test-id={icon.dataTestId} className={classes.icon} />}
        {bannerContent}
      </Paper>
      <Box position="relative">
        <Backdrop customClass="content" />
        {children}
      </Box>
    </>
  );
};

ContentBackdrop.propTypes = {
  bannerContent: PropTypes.node.isRequired,
  children: PropTypes.node,
  bannerMaxWidth: PropTypes.string,
  icon: PropTypes.shape({
    Component: PropTypes.elementType.isRequired,
    dataTestId: PropTypes.string
  })
};

export default ContentBackdrop;
