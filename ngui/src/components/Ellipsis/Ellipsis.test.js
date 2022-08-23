import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Ellipsis from "./Ellipsis";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Ellipsis />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
