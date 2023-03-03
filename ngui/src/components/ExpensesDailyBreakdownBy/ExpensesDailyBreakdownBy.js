import React from "react";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import WrapperCard from "components/WrapperCard";
import { AXIS_FORMATS } from "utils/charts";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import BreakdownBy from "./BreakdownBy";
import ExpensesDailyBreakdownByBarChart from "./ExpensesDailyBreakdownByBarChart";

const ExpensesDailyBreakdownBy = ({ breakdown, breakdownByValue, onBreakdownByChange, isLoading = false }) => (
  <WrapperCard>
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        <BreakdownBy value={breakdownByValue} onChange={onBreakdownByChange} />
      </Grid>
      <Grid item xs={12}>
        <ExpensesDailyBreakdownByBarChart
          dataTestId="expenses_breakdown_chart"
          breakdown={breakdown}
          breakdownBy={breakdownByValue}
          isLoading={isLoading}
          axisFormat={AXIS_FORMATS.MONEY}
        />
      </Grid>
    </Grid>
  </WrapperCard>
);

ExpensesDailyBreakdownBy.propTypes = {
  breakdown: PropTypes.objectOf(
    PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        cost: PropTypes.number.isRequired,
        name: PropTypes.string,
        type: PropTypes.string
      })
    )
  ).isRequired,
  breakdownByValue: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  onBreakdownByChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default ExpensesDailyBreakdownBy;
