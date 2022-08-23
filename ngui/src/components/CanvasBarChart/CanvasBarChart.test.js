import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CanvasBarChart from "./CanvasBarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CanvasBarChart data={[]} keys={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
