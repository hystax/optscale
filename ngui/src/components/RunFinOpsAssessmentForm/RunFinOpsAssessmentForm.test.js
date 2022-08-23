import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RunFinOpsAssessmentForm from "./RunFinOpsAssessmentForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RunFinOpsAssessmentForm onSubmit={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
