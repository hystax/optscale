import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceExpenses from "./ResourceExpenses";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceExpenses firstSeen={1622473475} lastSeen={1654687344} resourceId="e3272af1-cedd-4c5e-a318-197e4ea61b57" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
