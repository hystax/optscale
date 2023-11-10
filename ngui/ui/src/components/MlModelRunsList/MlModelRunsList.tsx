import { useMemo, useState } from "react";
import { Stack } from "@mui/material";
import LinearDatePicker from "components/LinearDatePicker";
import TableLoader from "components/TableLoader";
import useDateRanges, {
  allRange,
  customRange,
  oneDayRange,
  oneMonthRange,
  oneWeekRange,
  twoWeeksRange
} from "hooks/useDateRanges";
import { GOALS_FILTER, STATUS_FILTER } from "utils/constants";
import { secondsToMilliseconds, inDateRange } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import RunsBreakdowns from "./RunsBreakdowns";
import RunsFilters from "./RunsFilters";
import RunsTable from "./RunsTable";

const MlModelRunsList = ({ runs, isLoading }) => {
  const [appliedFilters, setAppliedFilters] = useState({});

  const { selectedRange, onSelectedRangeChange, ranges } = useDateRanges([
    allRange(true),
    oneDayRange(true),
    oneWeekRange(true),
    twoWeeksRange(true),
    oneMonthRange(true),
    customRange(true)
  ]);

  const { interval } = selectedRange;

  const filteredRuns = useMemo(() => {
    const filters = Object.entries(appliedFilters).filter(([, filterValue]) => filterValue !== undefined);

    return runs.filter((run) => {
      const checkDates = () => {
        const millisecondsRunStartTimestamp = secondsToMilliseconds(run.start);

        return inDateRange(
          {
            startDate: interval.startDate,
            endDate: interval.endDate
          },
          millisecondsRunStartTimestamp
        );
      };

      const checkFilters = () =>
        filters.every((filter) => {
          const [filterType, filterValue] = filter;

          if (filterType === GOALS_FILTER) {
            if (!run.reached_goals || isEmptyObject(run.reached_goals)) {
              return false;
            }
            return Object.values(run.reached_goals).every(({ reached }) => reached) === filterValue;
          }

          if (filterType === STATUS_FILTER) {
            return run.status === filterValue;
          }

          return false;
        });

      return checkDates() && checkFilters();
    });
  }, [appliedFilters, interval.endDate, interval.startDate, runs]);

  return (
    <Stack spacing={SPACING_2}>
      <RunsFilters
        datePicker={
          <LinearDatePicker selectedRange={selectedRange} onSelectedRangeChange={onSelectedRangeChange} ranges={ranges} />
        }
        runs={runs}
        onChange={setAppliedFilters}
        appliedFilters={appliedFilters}
        isLoading={isLoading}
      />
      <RunsBreakdowns runs={filteredRuns} isLoading={isLoading} />
      {isLoading ? <TableLoader columnsCounter={4} /> : <RunsTable runs={filteredRuns} />}
    </Stack>
  );
};

export default MlModelRunsList;
