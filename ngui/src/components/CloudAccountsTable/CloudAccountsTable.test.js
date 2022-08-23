import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CloudAccountsTable from "./CloudAccountsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudAccountsTable />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
