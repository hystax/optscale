import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CleanExpensesTable from "./CleanExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CleanExpensesTable expenses={[]} appliedFilters={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
