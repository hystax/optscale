import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PoolTypeSelector from "./PoolTypeSelector";

it("renders with action", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolTypeSelector />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
