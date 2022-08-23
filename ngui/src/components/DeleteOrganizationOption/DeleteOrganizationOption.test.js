import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DeleteOrganizationOption from "./DeleteOrganizationOption";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteOrganizationOption name="" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
