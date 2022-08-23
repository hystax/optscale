import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EditPoolPolicyLimitForm from "./EditPoolPolicyLimitForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EditPoolPolicyLimitForm />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
