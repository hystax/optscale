import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ApiMessage from "./ApiMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ApiMessage code="OEXXX" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
