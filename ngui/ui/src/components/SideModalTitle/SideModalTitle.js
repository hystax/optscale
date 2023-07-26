import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const SideModalTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h2" variant="h6" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

SideModalTitle.propTypes = {
  children: PropTypes.node.isRequired,
  dataProductTourId: PropTypes.string,
  dataTestId: PropTypes.string
};

export default SideModalTitle;
