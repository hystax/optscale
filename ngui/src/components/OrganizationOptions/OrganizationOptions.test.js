import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationOptions from "./OrganizationOptions";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationOptions expandedOption="" requestedOption="" value={{}} handleExpand={() => {}} options={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
