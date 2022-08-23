import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AnomalyRunChartCell from "./AnomalyRunChartCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AnomalyRunChartCell breakdown={{}} today={0} average={0} threshold={0} type={"type"} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
