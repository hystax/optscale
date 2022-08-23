import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MetricLegend from "./MetricLegend";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MetricLegend />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
