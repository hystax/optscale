import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceUsageFormattedNumber from "./ResourceUsageFormattedNumber";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceUsageFormattedNumber usage={0} unit="GB" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
