import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CollapsableTableCell from "./CollapsableTableCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CollapsableTableCell tags={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
