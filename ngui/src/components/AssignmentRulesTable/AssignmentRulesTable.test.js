import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AssignmentRulesTable from "./AssignmentRulesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AssignmentRulesTable assignmentRules={[]} organizationId="" entities={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
