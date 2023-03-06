import React from "react";
import PropTypes from "prop-types";
import { FormattedNumber } from "react-intl";
import CompactFormattedNumber from "components/CompactFormattedNumber";

const DynamicFractionDigitsValue = ({ value, maximumFractionDigits = 2, notation }) => {
  const props = {
    value,
    maximumFractionDigits
  };

  if (notation === "compact") {
    return <CompactFormattedNumber {...props} />;
  }

  return <FormattedNumber {...props} notation={notation} />;
};

DynamicFractionDigitsValue.propTypes = {
  value: PropTypes.number.isRequired,
  maximumFractionDigits: PropTypes.number,
  notation: PropTypes.string
};

export default DynamicFractionDigitsValue;
