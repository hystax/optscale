import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";

const TitleValue = React.forwardRef(({ children, dataTestId, style = {}, ...rest }, ref) => (
  <Typography
    component="span"
    variant="subtitle1"
    data-test-id={dataTestId}
    style={{ ...style, fontWeight: "bold" }}
    ref={ref}
    {...rest}
  >
    {children}
  </Typography>
));

TitleValue.propTypes = {
  children: PropTypes.node.isRequired,
  style: PropTypes.object,
  dataTestId: PropTypes.string
};

export default TitleValue;
