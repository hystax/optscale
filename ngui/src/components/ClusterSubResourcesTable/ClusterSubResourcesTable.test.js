import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ClusterSubResourcesTable from "./ClusterSubResourcesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ClusterSubResourcesTable />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
