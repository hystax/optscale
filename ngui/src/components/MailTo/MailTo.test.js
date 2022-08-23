import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MailTo from "./MailTo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MailTo email="test@test.com" text="test@test.com" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
