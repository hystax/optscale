import { Stack } from "@mui/material";
import LinearDatePicker from "components/LinearDatePicker";
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
import { SPACING_1 } from "utils/layouts";

const ExecutorsPanel = () => {
  const { selectedRange, onSelectedRangeChange, ranges } = useDateRanges([
    allRange(true),
    oneDayRange(true),
    oneWeekRange(true),
    twoWeeksRange(true),
    oneMonthRange(true),
    customRange(true)
  ]);

  return (
    <Stack spacing={SPACING_1}>
      <LinearDatePicker selectedRange={selectedRange} onSelectedRangeChange={onSelectedRangeChange} ranges={ranges} />
      <MlExecutorsBreakdownContainer dateRange={selectedRange.interval} />
      <MlExecutorsContainer dateRange={selectedRange.interval} />
    </Stack>
  );
};

export default ExecutorsPanel;
