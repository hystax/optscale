import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Slack from "./Slack";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Slack />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
