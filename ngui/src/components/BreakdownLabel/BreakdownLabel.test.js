import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";
import BreakdownLabel from "./BreakdownLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <BreakdownLabel breakdownBy={RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID} details={{ id: "id", name: "name" }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
