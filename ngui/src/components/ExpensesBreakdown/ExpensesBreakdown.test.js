import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { EXPENSES_FILTERBY_TYPES, COST_EXPLORER } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import ExpensesBreakdown from "./ExpensesBreakdown";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        rangeDates: {}
      }}
    >
      <ExpensesBreakdown
        entityId="entityId"
        filterBy={EXPENSES_FILTERBY_TYPES.CLOUD}
        type={COST_EXPLORER}
        breakdown={{}}
        total={0}
        previousTotal={0}
        filteredBreakdown={[]}
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        isLoading={false}
        onApply={jest.fn}
        updateFilter={jest.fn}
        name="name"
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
