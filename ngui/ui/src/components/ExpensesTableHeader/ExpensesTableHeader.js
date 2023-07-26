import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import TextWithDate from "components/TextWithDate";

const ExpensesTableHeader = ({ startDateTimestamp, endDateTimestamp }) => (
  <TextWithDate
    text={<FormattedMessage id="expenses" />}
    startDateTimestamp={startDateTimestamp}
    endDateTimestamp={endDateTimestamp}
  />
);

ExpensesTableHeader.propTypes = {
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number
};

export default ExpensesTableHeader;
