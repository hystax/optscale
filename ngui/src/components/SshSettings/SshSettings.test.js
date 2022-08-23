import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SshSettings from "./SshSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SshSettings />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
