import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import BarChart from "./BarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <BarChart data={[]} keys={[]} fieldTooltipText={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
