import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ExecutorsPanel from "./ExecutorsPanel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ExecutorsPanel />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
