import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SelectorLoader from "./SelectorLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SelectorLoader labelId="hystax" isRequired />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
