import { Grid } from "@mui/material";
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

export default ExpensesDailyBreakdown;
