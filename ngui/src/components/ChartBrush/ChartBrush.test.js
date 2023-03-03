import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ChartBrush from "./ChartBrush";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ChartBrush />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
