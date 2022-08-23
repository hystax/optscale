import React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

const PageLoader = () => (
  <Box top={0} left={0} right={0} bottom={0} display="flex" position="fixed" alignItems="center" justifyContent="center">
    <CircularProgress />
  </Box>
);

export default PageLoader;
