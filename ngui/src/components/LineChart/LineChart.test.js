import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import LineChart from "./LineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LineChart data={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
