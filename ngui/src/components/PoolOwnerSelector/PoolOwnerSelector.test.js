import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PoolOwnerSelector from "./PoolOwnerSelector";

const owners = [
  {
    id: "id",
    name: "Name",
    test: 123
  }
];

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolOwnerSelector owners={owners} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
