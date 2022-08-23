import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ExpensesDailyBreakdown from "./ExpensesDailyBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ExpensesDailyBreakdown />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
