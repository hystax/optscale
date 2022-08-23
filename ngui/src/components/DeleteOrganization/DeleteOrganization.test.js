import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DeleteOrganization from "./DeleteOrganization";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteOrganization />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
