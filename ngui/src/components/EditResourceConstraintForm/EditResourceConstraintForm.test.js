import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EditResourceConstraintForm from "./EditResourceConstraintForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EditResourceConstraintForm
        constraintType="ttl"
        constraintLimit={0}
        constraintId="id"
        onSubmit={jest.fn}
        onSuccess={jest.fn}
        onCancel={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
