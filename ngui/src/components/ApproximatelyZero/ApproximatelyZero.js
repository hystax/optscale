import React from "react";
import PropTypes from "prop-types";
import { FormattedNumber } from "react-intl";

export const formatApproximatelyZero =
  (formatter) =>
  ({ format }) =>
    `\u2248${formatter(0, { format })}`;

const ApproximatelyZero = ({ format }) => (
  <>
    &asymp;
    <FormattedNumber value={0} format={format} />
  </>
);

ApproximatelyZero.propTypes = {
  format: PropTypes.string
};

export default ApproximatelyZero;
