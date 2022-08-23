import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PoolTypesDescription from "./PoolTypesDescription";

it("renders with action", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolTypesDescription />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
