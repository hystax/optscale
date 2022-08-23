import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { SPACING_4 } from "utils/layouts";

const PageContentWrapper = ({ children }) => <Box padding={SPACING_4}>{children}</Box>;

PageContentWrapper.propTypes = {
  children: PropTypes.node
};

export default PageContentWrapper;
