import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CloudExpensesChart from "./CloudExpensesChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudExpensesChart cloudAccounts={[]} pool={123} forecast={234} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
