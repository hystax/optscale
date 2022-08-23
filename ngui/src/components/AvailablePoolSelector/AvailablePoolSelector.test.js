import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AvailablePoolSelector from "./AvailablePoolSelector";

const pools = [
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
      <AvailablePoolSelector pools={pools} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
