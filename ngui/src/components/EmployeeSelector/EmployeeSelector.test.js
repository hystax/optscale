import React from "react";
import { createRoot } from "react-dom/client";
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
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EmployeeSelector employees={employees} />
    </TestProvider>
  );
  root.unmount();
});
