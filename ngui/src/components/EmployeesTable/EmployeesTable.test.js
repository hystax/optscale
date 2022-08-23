import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EmployeesTable from "./EmployeesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EmployeesTable employees={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
