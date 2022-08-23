import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SplitResources from "./SplitResources";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider state={{ organizationId: "organizationId" }}>
      <SplitResources data={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
