import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceLifecycleGlobalPoolPoliciesContainerMocked from "./ResourceLifecycleGlobalPoolPoliciesContainerMocked";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceLifecycleGlobalPoolPoliciesContainerMocked />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
