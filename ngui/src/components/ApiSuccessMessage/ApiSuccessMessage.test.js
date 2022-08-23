import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ApiSuccessMessage from "./ApiSuccessMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ApiSuccessMessage successCode="FE0001" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
