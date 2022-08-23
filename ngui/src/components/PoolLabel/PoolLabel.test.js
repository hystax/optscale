import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PoolLabel from "./PoolLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolLabel name="name" type="type" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
