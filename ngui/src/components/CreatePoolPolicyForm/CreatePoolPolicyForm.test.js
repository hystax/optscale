import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CreatePoolPolicyForm from "./CreatePoolPolicyForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CreatePoolPolicyForm pools={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
