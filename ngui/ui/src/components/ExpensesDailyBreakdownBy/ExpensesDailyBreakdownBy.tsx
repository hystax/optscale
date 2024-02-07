import { Box, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import WrapperCard from "components/WrapperCard";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { DAILY_EXPENSES_SPLIT_PARAMETER_NAME } from "urls";
import { AXIS_FORMATS } from "utils/charts";
import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { SPLITS } from "utils/getResourceExpensesSplits";
import { SPACING_1 } from "utils/layouts";
import BreakdownBy from "./BreakdownBy";
import ExpensesDailyBreakdownByBarChart from "./ExpensesDailyBreakdownByBarChart";

const ExpensesDailyBreakdownBy = ({ breakdown, breakdownByValue, onBreakdownByChange, isLoading = false }) => {
  const [split, setSplit] = useSyncQueryParamWithState({
    queryParamName: DAILY_EXPENSES_SPLIT_PARAMETER_NAME,
    possibleStates: SPLITS,
    defaultValue: EXPENSES_SPLIT_PERIODS.DAILY
  });

  return (
    <WrapperCard>
      <Stack spacing={SPACING_1}>
        <Box display="flex" gap={1}>
          <BreakdownBy value={breakdownByValue} onChange={onBreakdownByChange} />
          <Selector id="expenses-split-selector" labelMessageId="expenses" value={split} onChange={setSplit}>
            {SPLITS.map((splitValue) => (
              <Item key={splitValue} value={splitValue}>
                <ItemContent>
                  <FormattedMessage id={splitValue} />
                </ItemContent>
              </Item>
            ))}
          </Selector>
        </Box>
        <div>
          <ExpensesDailyBreakdownByBarChart
            dataTestId="expenses_breakdown_chart"
            breakdown={breakdown}
            breakdownBy={breakdownByValue}
            isLoading={isLoading}
            split={split}
            axisFormat={AXIS_FORMATS.MONEY}
          />
        </div>
      </Stack>
    </WrapperCard>
  );
};

export default ExpensesDailyBreakdownBy;
