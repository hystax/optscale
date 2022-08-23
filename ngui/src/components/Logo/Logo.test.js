import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Logo from "./Logo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Logo />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
