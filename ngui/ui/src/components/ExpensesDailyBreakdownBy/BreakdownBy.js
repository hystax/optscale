import React from "react";
import PropTypes from "prop-types";
import Selector from "components/Selector";
import { breakdowns } from "hooks/useBreakdownBy";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";

const BreakdownBy = ({ value, onChange }) => (
  <Selector
    data={{
      selected: value,
      items: breakdowns
    }}
    labelId="categorizeBy"
    onChange={onChange}
  />
);

BreakdownBy.propTypes = {
  value: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  onChange: PropTypes.func.isRequired
};

export default BreakdownBy;
