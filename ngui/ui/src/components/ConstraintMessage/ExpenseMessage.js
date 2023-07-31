import React from "react";
import PropTypes from "prop-types";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";

const ExpenseMessage = ({ type, limit }) => (
  <TextWithDataTestId dataTestId={`p_${type}_value`}>
    <FormattedMoney value={limit} />
  </TextWithDataTestId>
);

ExpenseMessage.propTypes = {
  type: PropTypes.string.isRequired,
  limit: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
};

export default ExpenseMessage;
