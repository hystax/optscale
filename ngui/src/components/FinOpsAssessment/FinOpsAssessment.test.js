import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import FinOpsAssessment from "./FinOpsAssessment";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <FinOpsAssessment />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
