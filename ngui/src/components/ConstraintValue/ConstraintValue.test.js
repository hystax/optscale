import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ConstraintValue from "./ConstraintValue";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ConstraintValue hitValue={120} constraintLimit={100} type="test" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
