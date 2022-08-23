import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceConstraints from "./ResourceConstraints";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceConstraints resourceId="id" constraints={{}} poolPolicies={{}} isLoading={false} billingOnly={false} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
