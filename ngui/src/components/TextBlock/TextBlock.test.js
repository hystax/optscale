import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TextBlock from "./TextBlock";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TextBlock messageId="test" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
