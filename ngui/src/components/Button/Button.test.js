import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Button from "./Button";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Button messageId="hystax" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
