import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DataSourceNodes from "./DataSourceNodes";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DataSourceNodes cloudAccountId="cloudAccountId" costModel={{}} nodes={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
