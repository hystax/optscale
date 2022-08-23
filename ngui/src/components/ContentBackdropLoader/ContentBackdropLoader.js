import React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import PropTypes from "prop-types";
import Backdrop from "components/Backdrop";

const ContentBackdropLoader = ({ isLoading = false, children }) => (
  <Box height="100%" position="relative">
    {isLoading && (
      <Backdrop customClass="contentLoader">
        <CircularProgress />
      </Backdrop>
    )}
    {children}
  </Box>
);

ContentBackdropLoader.propTypes = {
  children: PropTypes.node,
  isLoading: PropTypes.bool
};

export default ContentBackdropLoader;
