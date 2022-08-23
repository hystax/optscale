import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import K8sRightsizingTable from "./K8sRightsizingTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <K8sRightsizingTable namespaces={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
