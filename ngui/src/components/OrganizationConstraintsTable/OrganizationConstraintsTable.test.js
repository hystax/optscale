import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationConstraintsTable from "./OrganizationConstraintsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationConstraintsTable constraints={[]} addButtonLink="" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
