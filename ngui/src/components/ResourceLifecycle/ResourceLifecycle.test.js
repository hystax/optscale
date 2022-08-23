import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceLifecycle from "./ResourceLifecycle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceLifecycle />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
