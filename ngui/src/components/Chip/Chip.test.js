import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Chip from "./Chip";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Chip />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
