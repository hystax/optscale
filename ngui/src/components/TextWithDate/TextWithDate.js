import React from "react";
import PropTypes from "prop-types";
import { formatRangeToShortNotation } from "utils/datetime";

// renders "short daterange format" surrounded by space and brackets: " (%DATERANGE%)"
const TextWithDate = ({ text, startDateTimestamp, endDateTimestamp }) => (
  <>
    {text}
    {startDateTimestamp && endDateTimestamp && <>&nbsp;({formatRangeToShortNotation(startDateTimestamp, endDateTimestamp)})</>}
  </>
);

TextWithDate.propTypes = {
  text: PropTypes.node.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number
};

export default TextWithDate;
