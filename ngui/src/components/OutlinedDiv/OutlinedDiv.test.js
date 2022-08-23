import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OutlinedDiv from "./OutlinedDiv";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OutlinedDiv />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
