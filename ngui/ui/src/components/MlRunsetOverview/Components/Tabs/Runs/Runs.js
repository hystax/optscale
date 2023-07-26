import React, { useEffect, useMemo, useState } from "react";
import { Stack } from "@mui/material";
import { ML_RUNS_FILTERS_NAMES } from "components/Filters/constants";
import { GOALS_BE_FILTER, GOALS_FILTER, GOAL_STATUS, STATUS_BE_FILTER } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";
import RunsFilter from "./RunsFilter";
import RunsTable from "./RunsTable";

const Runs = ({ runs, isLoading = false }) => {
  const [appliedFilters, setAppliesFilters] = useState(() => {
    const queryParams = getQueryParams();

    return ML_RUNS_FILTERS_NAMES.reduce(
      (params, queryKey) => ({
        ...params,
        [queryKey]: queryParams[queryKey]
      }),
      {}
    );
  });

  const filterValues = {
    [STATUS_BE_FILTER]: [
      ...new Map(
        runs.map(({ status }) => [
          status,
          {
            name: status
          }
        ])
      ).values()
    ],
    [GOALS_BE_FILTER]: [
      {
        name: GOAL_STATUS.MET,
        value: true
      },
      {
        name: GOAL_STATUS.NOT_MET,
        value: false
      }
    ]
  };

  useEffect(() => {
    updateQueryParams(appliedFilters);
  }, [appliedFilters]);

  const onFilterChange = (newFilters) => setAppliesFilters(newFilters);

  const filteredRuns = useMemo(() => {
    const filters = Object.entries(appliedFilters).filter(([, filterValue]) => filterValue !== undefined);

    if (filters.length === 0) return runs;

    return runs.filter((run) =>
      filters.every((filter) => {
        const [filterType, filterValue] = filter;

        if (filterType === GOALS_FILTER) {
          if (!run.reached_goals || isEmptyObject(run.reached_goals)) {
            return false;
          }
          return Object.values(run.reached_goals).every(({ reached }) => reached) === filterValue;
        }

        if (filterType === STATUS_BE_FILTER) {
          return run.status === filterValue;
        }

        return false;
      })
    );
  }, [appliedFilters, runs]);

  return (
    <Stack spacing={SPACING_1}>
      <div>
        <RunsFilter
          appliedFilters={appliedFilters}
          filterValues={filterValues}
          onChange={onFilterChange}
          isLoading={isLoading}
        />
      </div>
      <div>
        <RunsTable runs={filteredRuns} isLoading={isLoading} />
      </div>
    </Stack>
  );
};

export default Runs;
