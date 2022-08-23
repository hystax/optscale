import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { SPACING_1 } from "utils/layouts";

// TODO - check why table does not inherit variant size everywhere, on;y on OrganizationOverview
const TabContent = ({ children, variant, value, index, id, ariaLabelledby, ...rest }) => (
  <Typography
    component="div"
    role="tabpanel"
    hidden={value !== index}
    id={id}
    aria-labelledby={ariaLabelledby}
    variant={variant}
    {...rest}
    style={{ paddingTop: `${SPACING_1}rem` }}
  >
    {children}
  </Typography>
);

// TODO - fix props from string to number
TabContent.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  index: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  id: PropTypes.string,
  ariaLabelledby: PropTypes.string,
  children: PropTypes.node,
  variant: PropTypes.string
};

export default TabContent;
