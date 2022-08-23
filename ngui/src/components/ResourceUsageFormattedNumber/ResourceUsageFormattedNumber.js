import React from "react";
import PropTypes from "prop-types";
import { FormattedNumber } from "react-intl";

const ResourceUsageFormattedNumber = ({ usage, unit }) => (
  <span>
    <FormattedNumber value={usage} maximumFractionDigits={2} /> {unit}
  </span>
);

ResourceUsageFormattedNumber.propTypes = {
  usage: PropTypes.number.isRequired,
  unit: PropTypes.string.isRequired
};

export default ResourceUsageFormattedNumber;
