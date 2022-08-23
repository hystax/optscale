import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EditablePoolPolicyLimit from "./EditablePoolPolicyLimit";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EditablePoolPolicyLimit />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
