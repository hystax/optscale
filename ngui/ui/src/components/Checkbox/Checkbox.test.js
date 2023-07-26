import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Checkbox from "./Checkbox";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Checkbox />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
