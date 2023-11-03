import React from "react";
import PropTypes from "prop-types";

const IconLabel = ({ icon: startIcon, endIcon, label }) => (
  <div style={{ display: "inline-flex", verticalAlign: "middle", alignItems: "center" }}>
    {startIcon && <>{startIcon}&nbsp;</>}
    {label}
    {endIcon && <>&nbsp;{endIcon}</>}
  </div>
);

IconLabel.propTypes = {
  icon: PropTypes.node,
  endIcon: PropTypes.node,
  label: PropTypes.any.isRequired
};

export default IconLabel;
