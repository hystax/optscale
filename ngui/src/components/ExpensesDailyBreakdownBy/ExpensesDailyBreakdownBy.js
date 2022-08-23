import React from "react";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import { AXIS_FORMATS } from "utils/charts";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import BarChart from "./BarChart";
import BreakdownBy from "./BreakdownBy";

const ExpensesDailyBreakdownBy = ({ breakdown, breakdownBy, onBreakdownByChange, isLoading = false }) => (
  <Grid container spacing={SPACING_1}>
    <Grid item xs={12} sx={{ display: "flex", justifyContent: "flex-end" }}>
      <BreakdownBy value={breakdownBy} onChange={onBreakdownByChange} />
    </Grid>
    <Grid item xs={12}>
      <BarChart breakdown={breakdown} breakdownBy={breakdownBy} isLoading={isLoading} axisFormat={AXIS_FORMATS.MONEY} />
    </Grid>
  </Grid>
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
  breakdownBy: PropTypes.oneOf(RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES).isRequired,
  onBreakdownByChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default ExpensesDailyBreakdownBy;
