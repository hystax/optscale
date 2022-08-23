import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MetricChart from "./MetricChart";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MetricChart lines={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
