import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import JiraIssuesAttachments from "./JiraIssuesAttachments";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <JiraIssuesAttachments />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
