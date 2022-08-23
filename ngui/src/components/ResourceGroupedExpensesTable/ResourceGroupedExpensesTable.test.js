import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceGroupedExpensesTable from "./ResourceGroupedExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceGroupedExpensesTable data={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
