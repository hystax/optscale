import { RefObject, useRef } from "react";
import { Box, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ChartExport from "components/ChartExport";
import ChartLegendToggle from "components/ChartLegendToggle/ChartLegendToggle";
import Selector, { Item, ItemContent } from "components/Selector";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { DAILY_EXPENSES_SPLIT_PARAMETER_NAME, WITH_LEGEND_QUERY_PARAMETER_NAME } from "urls";
import { AXIS_FORMATS } from "utils/charts";
import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { SPLITS } from "utils/getResourceExpensesSplits";
import { SPACING_1 } from "utils/layouts";
import BreakdownBy from "./BreakdownBy";
import ExpensesDailyBreakdownByBarChart from "./ExpensesDailyBreakdownByBarChart";

type Breakdown = {
  id: string;
  cost: number;
};

type Breakdowns = {
  [key: number]: Breakdown[];
};

type Count = {
  total: number;
  previous_total: number;
};

type ExpensesDailyBreakdownByProps = {
  counts: { [key: string]: Count };
  breakdown: Breakdowns;
  breakdownByValue: string;
  onBreakdownByChange: () => void;
  isLoading: boolean;
};

const ExpensesDailyBreakdownBy = ({
  counts,
  breakdown,
  breakdownByValue,
  onBreakdownByChange,
  isLoading = false,
}: ExpensesDailyBreakdownByProps) => {
  const chartWrapperRef: RefObject<HTMLElement | null> = useRef(null);

  const [split, setSplit] = useSyncQueryParamWithState({
    queryParamName: DAILY_EXPENSES_SPLIT_PARAMETER_NAME,
    possibleStates: SPLITS,
    defaultValue: EXPENSES_SPLIT_PERIODS.DAILY,
  });

  const [withLegend, setWithLegend] = useSyncQueryParamWithState({
    queryParamName: WITH_LEGEND_QUERY_PARAMETER_NAME,
    possibleStates: [true, false],
    defaultValue: true,
  });

  return (
    <Stack spacing={SPACING_1}>
      <Box display="flex" alignItems="center" justifyContent="space-between">
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
          <ChartLegendToggle checked={withLegend} onChange={setWithLegend} />
        </Box>
        <ChartExport chartWrapperRef={chartWrapperRef} isLoading={isLoading} />
      </Box>
      <Box>
        <ExpensesDailyBreakdownByBarChart
          dataTestId="expenses_breakdown_chart"
          chartWrapperRef={chartWrapperRef}
          breakdown={breakdown}
          breakdownBy={breakdownByValue}
          showLegend={withLegend}
          counts={counts}
          isLoading={isLoading}
          split={split}
          axisFormat={AXIS_FORMATS.MONEY}
        />
      </Box>
    </Stack>
  );
};

export default ExpensesDailyBreakdownBy;
