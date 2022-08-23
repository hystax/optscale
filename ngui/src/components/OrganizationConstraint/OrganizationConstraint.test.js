import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationConstraint from "./OrganizationConstraint";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationConstraint actionBarTitleDefinition={{}} constraint={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
