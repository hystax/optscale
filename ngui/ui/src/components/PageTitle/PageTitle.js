import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const PageTitle = React.forwardRef(({ children, dataProductTourId, dataTestId, ...rest }, ref) => (
  <Typography
    component="h1"
    variant="h6"
    data-product-tour-id={dataProductTourId}
    data-test-id={dataTestId}
    ref={ref}
    {...rest}
  >
    {children}
  </Typography>
));

PageTitle.propTypes = {
  children: PropTypes.node.isRequired,
  dataProductTourId: PropTypes.string,
  dataTestId: PropTypes.string
};

export default PageTitle;
