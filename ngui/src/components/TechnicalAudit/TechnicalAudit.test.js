import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TechnicalAudit from "./TechnicalAudit";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TechnicalAudit />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
