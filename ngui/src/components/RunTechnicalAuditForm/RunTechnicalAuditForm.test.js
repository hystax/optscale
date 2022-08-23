import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RunTechnicalAuditForm from "./RunTechnicalAuditForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RunTechnicalAuditForm onSubmit={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
