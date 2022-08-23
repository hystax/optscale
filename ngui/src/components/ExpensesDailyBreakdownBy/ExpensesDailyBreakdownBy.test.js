import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";
import ExpensesDailyBreakdownBy from "./ExpensesDailyBreakdownBy";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ExpensesDailyBreakdownBy
        breakdown={{}}
        breakdownBy={RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID}
        onBreakdownByChange={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
