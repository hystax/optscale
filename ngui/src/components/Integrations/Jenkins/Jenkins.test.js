import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Jenkins from "./Jenkins";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Jenkins />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
