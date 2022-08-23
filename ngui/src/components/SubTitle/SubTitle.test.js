import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SubTitle from "./SubTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SubTitle />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
