import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Jira from "./Jira";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Jira totalEmployees={0} connectedEmployees={0} isCurrentEmployeeConnectedToJira connectedWorkspaces={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
