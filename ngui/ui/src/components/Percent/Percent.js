import React from "react";
import PropTypes from "prop-types";
import { FormattedNumber } from "react-intl";

const BORDER_PERCENT = 5;

const Percent = (props) => {
  let { value = 0 } = props;
  value = Math.abs(value);
  if (value < BORDER_PERCENT) {
    value = Math.round(value * 10) / 10;
  } else {
    value = Math.round(value);
  }

  return (
    <>
      <FormattedNumber value={value} />%
    </>
  );
};

Percent.propTypes = {
  value: PropTypes.number.isRequired
};

export default Percent;
