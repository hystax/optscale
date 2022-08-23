import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ChartTooltip from "./ChartTooltip";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ChartTooltip />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
