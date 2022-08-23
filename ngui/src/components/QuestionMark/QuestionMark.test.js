import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import QuestionMark from "./QuestionMark";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <QuestionMark messageId="name" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
