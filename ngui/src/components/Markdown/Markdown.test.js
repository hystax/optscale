import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Markdown from "./Markdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Markdown value="123" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
