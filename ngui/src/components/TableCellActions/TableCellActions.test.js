import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TableCellActions from "./TableCellActions";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TableCellActions items={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
