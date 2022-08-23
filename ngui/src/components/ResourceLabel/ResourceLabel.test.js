import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceLabel from "./ResourceLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceLabel cloudResourceId="cloudResourceId" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
