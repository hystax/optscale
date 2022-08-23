import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import KeyValueLabel from "./KeyValueLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <KeyValueLabel messageId="name" value="value" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
