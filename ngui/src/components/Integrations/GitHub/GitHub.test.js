import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import GitHub from "./GitHub";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <GitHub />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
