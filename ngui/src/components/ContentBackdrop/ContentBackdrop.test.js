import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ContentBackdrop from "./ContentBackdrop";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ContentBackdrop messageType="cloudAccounts" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
