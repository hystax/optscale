import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { SPACING_2 } from "utils/layouts";

const ExpensesBreakdownLayoutWrapper = ({ top, center: { left: centerLeft, right: centerRight }, bottom }) => (
  <Grid container direction="row" justifyContent="space-between" spacing={SPACING_2}>
    {top}
    <Grid item container spacing={SPACING_2}>
      {centerLeft && (
        <Grid item xs={12} md={centerRight ? 9 : 12}>
          {centerLeft}
        </Grid>
      )}
      {centerRight ? (
        <Grid item xs={12} md={3}>
          {centerRight}
        </Grid>
      ) : null}
    </Grid>
    {bottom && (
      <Grid item xs={12}>
        {bottom}
      </Grid>
    )}
  </Grid>
);

ExpensesBreakdownLayoutWrapper.propTypes = {
  bottom: PropTypes.node,
  center: PropTypes.shape({
    left: PropTypes.node,
    right: PropTypes.node
  }),
  top: PropTypes.node
};

export default ExpensesBreakdownLayoutWrapper;
