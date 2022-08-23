import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Day from "./Day";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Day />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
