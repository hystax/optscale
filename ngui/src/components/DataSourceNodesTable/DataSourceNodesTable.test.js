import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DataSourceNodesTable from "./DataSourceNodesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DataSourceNodesTable nodes={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
