import React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import PropTypes from "prop-types";
import Backdrop from "components/Backdrop";

const ContentBackdropLoader = ({ isLoading = false, size, children }) => (
  <Box height="100%" position="relative">
    {isLoading && (
      <Backdrop customClass="contentLoader">
        <CircularProgress size={size} />
      </Backdrop>
    )}
    {children}
  </Box>
);

ContentBackdropLoader.propTypes = {
  children: PropTypes.node,
  isLoading: PropTypes.bool,
  size: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
};

export default ContentBackdropLoader;
