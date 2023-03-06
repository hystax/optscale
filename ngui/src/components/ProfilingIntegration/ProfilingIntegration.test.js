import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ProfilingIntegration from "./ProfilingIntegration";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ProfilingIntegration />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
