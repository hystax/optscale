import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EmployeeSelector from "./EmployeeSelector";

const employees = [
  {
    id: "id",
    name: "Name",
    test: 123
  }
];

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EmployeeSelector employees={employees} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
