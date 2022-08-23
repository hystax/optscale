import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ClusterTypesTable from "./ClusterTypesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ClusterTypesTable clusterTypes={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
