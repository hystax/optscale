import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

const FromToArrowLabel = ({ from, to, strong = false }) => {
  const label = <FormattedMessage id="value -> value" values={{ value1: from, value2: to }} />;

  return strong ? <strong>{label}</strong> : label;
};

FromToArrowLabel.propTypes = {
  from: PropTypes.node.isRequired,
  to: PropTypes.node.isRequired,
  strong: PropTypes.bool
};

export default FromToArrowLabel;
