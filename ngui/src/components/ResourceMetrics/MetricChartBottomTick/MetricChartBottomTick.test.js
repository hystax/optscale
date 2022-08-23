import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MetricChartBottomTick from "./MetricChartBottomTick";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MetricChartBottomTick tick={{ value: Date.now() }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
