import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TopResourcesExpensesCard from "./TopResourcesExpensesCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TopResourcesExpensesCard cleanExpenses={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
