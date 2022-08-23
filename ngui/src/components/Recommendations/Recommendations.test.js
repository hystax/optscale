import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Recommendations from "./Recommendations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Recommendations />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
