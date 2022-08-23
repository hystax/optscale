import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import HeartLineChart from "./HeartLineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <HeartLineChart values={[0]} redZoneValue={0} average={0} width={100} height={100} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
