import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ThemeSettings from "./ThemeSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ThemeSettings />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
