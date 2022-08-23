import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ClusterTypes from "./ClusterTypes";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ClusterTypes clusterTypes={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
