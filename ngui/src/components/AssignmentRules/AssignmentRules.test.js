import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AssignmentRules from "./AssignmentRules";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AssignmentRules rules={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
