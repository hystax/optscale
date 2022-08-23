import React from "react";
import PropTypes from "prop-types";

const IconLabel = ({ icon, label }) => (
  <div style={{ display: "inline-flex", verticalAlign: "middle", alignItems: "center" }}>
    {icon}
    {label}
  </div>
);

IconLabel.propTypes = {
  icon: PropTypes.node.isRequired,
  label: PropTypes.any.isRequired
};

export default IconLabel;
