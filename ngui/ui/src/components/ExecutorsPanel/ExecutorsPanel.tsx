import { Box, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import LinearDatePicker from "components/LinearDatePicker";
import LinearSelector from "components/LinearSelector";
import MlExecutorsBreakdownContainer from "containers/MlExecutorsBreakdownContainer";
import MlExecutorsContainer from "containers/MlExecutorsContainer";
import useDateRanges, {
  allRange,
  oneDayRange,
  oneWeekRange,
  twoWeeksRange,
  oneMonthRange,
  customRange
} from "hooks/useDateRanges";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import {
  LINEAR_SELECTOR_ITEMS_TYPES,
  ML_EXECUTORS_DAILY_BREAKDOWN_BY,
  ML_EXECUTORS_BREAKDOWN_BY_MESSAGES,
  ML_MODEL_RUN_DAILY_BREAKDOWN_BY_VALUES
} from "utils/constants";
import { SPACING_4 } from "utils/layouts";

const breakdownLinearSelectorItems = Object.entries(ML_EXECUTORS_DAILY_BREAKDOWN_BY).map(([key, value]) => ({
  name: ML_EXECUTORS_BREAKDOWN_BY_MESSAGES[key],
  value,
  type: LINEAR_SELECTOR_ITEMS_TYPES.TEXT,
  dataTestId: `breakdown_ls_item_${key}`
}));

const ExecutorsPanel = () => {
  const { selectedRange, onSelectedRangeChange, ranges } = useDateRanges([
    allRange(true),
    oneDayRange(true),
    oneWeekRange(true),
    twoWeeksRange(true),
    oneMonthRange(true),
    customRange(true)
  ]);

  const [breakdownByQuery, setBreakdownByQuery] = useSyncQueryParamWithState({
    queryParamName: "breakdownBy",
    possibleStates: ML_MODEL_RUN_DAILY_BREAKDOWN_BY_VALUES,
    defaultValue: ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU
  });

  return (
    <Stack>
      <div>
        <Box mr={SPACING_4} display="inline-block">
          <LinearDatePicker selectedRange={selectedRange} onSelectedRangeChange={onSelectedRangeChange} ranges={ranges} />
        </Box>
        <LinearSelector
          value={breakdownLinearSelectorItems.find(({ value }) => value === breakdownByQuery)}
          label={<FormattedMessage id="chart" />}
          onChange={({ value }) => {
            setBreakdownByQuery(value);
          }}
          items={breakdownLinearSelectorItems}
          dataTestIds={{
            label: "ls_lbl_group"
          }}
        />
      </div>
      <MlExecutorsBreakdownContainer dateRange={selectedRange.interval} breakdownBy={breakdownByQuery} />
      <MlExecutorsContainer dateRange={selectedRange.interval} />
    </Stack>
  );
};

export default ExecutorsPanel;
