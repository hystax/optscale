import React from "react";
import { FormControlLabel, Grid, Switch, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useInScopeOfPageMockup } from "hooks/useInScopeOfPageMockup";
import { useShowExpensesDailyBreakdown } from "hooks/useShowExpensesDailyBreakdown";
import { SPACING_1 } from "utils/layouts";

const ExpensesDailyBreakdown = ({ container, mockup }) => {
  const [showExpensesDailyBreakdown, onShowExpensesDailyBreakdownChange] = useShowExpensesDailyBreakdown();

  const inScopeOfPageMockup = useInScopeOfPageMockup();

  const getContent = () => {
    const getElement = () => {
      if (inScopeOfPageMockup) {
        return mockup;
      }
      if (showExpensesDailyBreakdown) {
        return container;
      }
      return null;
    };

    if (inScopeOfPageMockup || showExpensesDailyBreakdown) {
      return (
        <Grid item xs={12}>
          {getElement()}
        </Grid>
      );
    }
    return null;
  };

  return (
    <Grid container spacing={SPACING_1}>
      <Grid
        item
        xs={12}
        sx={{
          display: "flex",
          justifyContent: "flex-end"
        }}
      >
        <FormControlLabel
          control={
            <Switch
              checked={showExpensesDailyBreakdown}
              onChange={(e) => onShowExpensesDailyBreakdownChange(e.target.checked)}
            />
          }
          label={
            <Typography>
              <FormattedMessage id="dailyExpensesChart" />
            </Typography>
          }
          labelPlacement="start"
        />
      </Grid>
      {getContent()}
    </Grid>
  );
};

ExpensesDailyBreakdown.propTypes = {
  container: PropTypes.node.isRequired,
  mockup: PropTypes.node.isRequired
};

export default ExpensesDailyBreakdown;
