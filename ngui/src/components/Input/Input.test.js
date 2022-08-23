import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Input from "./Input";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Input />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
