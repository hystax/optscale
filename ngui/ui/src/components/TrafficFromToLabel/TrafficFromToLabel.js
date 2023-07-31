import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

const TrafficFromToLabel = ({ from, to }) => (
  <FormattedMessage
    id="filterFromTo"
    values={{
      from,
      to,
      strong: (chunks) => <strong>{chunks}</strong>
    }}
  />
);

TrafficFromToLabel.propTypes = {
  from: PropTypes.string,
  to: PropTypes.string
};

export default TrafficFromToLabel;
