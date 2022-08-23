import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SomethingWentWrong from "./SomethingWentWrong";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SomethingWentWrong />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
