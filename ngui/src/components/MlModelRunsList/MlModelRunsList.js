import React, { useMemo, useState } from "react";
import { Stack } from "@mui/material";
import PropTypes from "prop-types";
import { checkGoalsFilter } from "components/Filters/GoalsFilter/GoalsFilter";
import LinearDatePicker from "components/LinearDatePicker";
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
import RunsChart from "./RunsChart";
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
            if (run.goals.length === 0) {
              return false;
            }
            return checkGoalsFilter[filterValue](
              run.goals.map((goal) => ({
                value: run.data?.[goal.key],
                tendency: goal.tendency,
                targetValue: goal.target_value
              }))
            );
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
      <RunsChart runs={filteredRuns} isLoading={isLoading} />
      <RunsTable runs={filteredRuns} isLoading={isLoading} />
    </Stack>
  );
};

MlModelRunsList.propTypes = {
  runs: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default MlModelRunsList;
