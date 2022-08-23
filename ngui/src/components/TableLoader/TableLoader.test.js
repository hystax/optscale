import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TableLoader from "./TableLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TableLoader columnsCounter={3} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
