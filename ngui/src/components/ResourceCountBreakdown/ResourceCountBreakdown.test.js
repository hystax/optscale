import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceCountBreakdown from "./ResourceCountBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceCountBreakdown countKeys={[]} counts={{}} breakdown={{}} appliedRange={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
