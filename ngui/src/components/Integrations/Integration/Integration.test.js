import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Integration from "./Integration";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Integration title={<div>title</div>} blocks={[<div key="block">block</div>]} id="integrationId" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
