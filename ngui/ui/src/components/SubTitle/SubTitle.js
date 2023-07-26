import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const SubTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h4" variant="subtitle1" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

SubTitle.propTypes = {
  children: PropTypes.node.isRequired,
  dataProductTourId: PropTypes.string,
  dataTestId: PropTypes.string
};

export default SubTitle;
