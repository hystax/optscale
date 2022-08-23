import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TrafficFromToLabel from "./TrafficFromToLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TrafficFromToLabel />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
