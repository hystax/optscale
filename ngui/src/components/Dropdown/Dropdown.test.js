import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Dropdown from "./Dropdown";

const items = [
  {
    key: "key"
  }
];

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Dropdown messageId="hystax" trigger="button" items={items} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
