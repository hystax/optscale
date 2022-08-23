import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import GitLab from "./GitLab";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <GitLab />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
