import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RightsizingCpuUsageHeaderCell from "./RightsizingCpuUsageHeaderCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RightsizingCpuUsageHeaderCell options={{ days_threshold: 1 }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
