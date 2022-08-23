import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CopyText from "./CopyText";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CopyText text="text">text</CopyText>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
