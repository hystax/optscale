import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationConstraints from "./OrganizationConstraints";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationConstraints actionBarDefinition={{}} constraints={[]} addButtonLink="" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
