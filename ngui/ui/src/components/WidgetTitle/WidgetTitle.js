import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const WidgetTitle = ({ children, dataProductTourId, dataTestId, ...rest }) => (
  <Typography component="h3" variant="subtitle1" data-product-tour-id={dataProductTourId} data-test-id={dataTestId} {...rest}>
    {children}
  </Typography>
);

WidgetTitle.propTypes = {
  children: PropTypes.node.isRequired,
  dataProductTourId: PropTypes.string,
  dataTestId: PropTypes.string
};

export default WidgetTitle;
