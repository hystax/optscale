import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Pagination from "./Pagination";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Pagination count={1} limit={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
