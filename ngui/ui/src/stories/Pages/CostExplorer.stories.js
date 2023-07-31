import React from "react";
import CostExplorer from "components/CostExplorer";
import { KINDS } from "stories";
import { millisecondsToSeconds } from "utils/datetime";

export default {
  title: `${KINDS.PAGES}/CostExplorer`
};

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

const expenses = {
  total: 352000,
  previousTotal: 252000,
  id: "e1a34742-1531-4b68-b52a-d1d438e52b68",
  name: "FutureOps.com",
  breakdown: {
    [firstDateRangePoint]: [
      {
        name: "expenses",
        expense: 180000
      }
    ],
    [lastDateRangePoint]: [
      {
        name: "expenses",
        expense: 172000
      }
    ]
  }
};

const onApply = () => console.log("Apply");

export const basic = () => (
  <CostExplorer
    total={expenses.total}
    previousTotal={expenses.previousTotal}
    breakdown={expenses.breakdown}
    organizationName={expenses.name}
    isLoading={false}
    onApply={onApply}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
  />
);

export const withoutBarChart = () => (
  <CostExplorer
    total={expenses.total}
    previousTotal={expenses.previousTotal}
    breakdown={{}}
    organizationName={expenses.name}
    isLoading={false}
    onApply={onApply}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
  />
);

export const loading = () => (
  <CostExplorer
    total={expenses.total}
    previousTotal={expenses.previousTotal}
    breakdown={{}}
    organizationName={expenses.name}
    isLoading
    onApply={onApply}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
  />
);
