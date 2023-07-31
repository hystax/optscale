import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Tour from "./Tour";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Tour />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
