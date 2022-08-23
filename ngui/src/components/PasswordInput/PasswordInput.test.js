import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PasswordInput from "./PasswordInput";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PasswordInput />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
