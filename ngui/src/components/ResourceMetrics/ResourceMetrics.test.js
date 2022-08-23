import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceMetrics from "./ResourceMetrics";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceMetrics metrics={{}} />
    </TestProvider>,
    div
  );

  ReactDOM.unmountComponentAtNode(div);
});
