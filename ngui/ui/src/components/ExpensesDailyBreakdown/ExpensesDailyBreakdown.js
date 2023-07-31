import React from "react";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { SPACING_1 } from "utils/layouts";

const ExpensesDailyBreakdown = ({ container, mockup }) => {
  const inScopeOfPageMockup = useInScopeOfPageMockup();

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {inScopeOfPageMockup ? mockup : container}
      </Grid>
    </Grid>
  );
};

ExpensesDailyBreakdown.propTypes = {
  container: PropTypes.node.isRequired,
  mockup: PropTypes.node.isRequired
};

export default ExpensesDailyBreakdown;
