import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { CLEAN_EXPENSES_BREAKDOWN_TYPES, RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import Resources from "./Resources";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Resources
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        filters={{}}
        filterValues={{}}
        onApply={jest.fn}
        onFilterAdd={jest.fn}
        onFilterDelete={jest.fn}
        onFiltersDelete={jest.fn}
        requestParams={{}}
        activeBreakdown={{
          name: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
          value: "expenses"
        }}
        expensesBreakdownPageState={{
          breakdownBy: [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID, null],
          groupBy: [{}, null]
        }}
        resourceCountBreakdownPageState={{
          breakdownBy: [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID, null]
        }}
        perspectives={{}}
        onBreakdownChange={jest.fn}
        onPerspectiveApply={jest.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
