import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Tooltip from "./Tooltip";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Tooltip title="title">
        <span>Content</span>
      </Tooltip>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
