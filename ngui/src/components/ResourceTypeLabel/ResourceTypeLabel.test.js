import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceTypeLabel from "./ResourceTypeLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceTypeLabel resourceInfo={{ resourceType: "resource_type" }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
