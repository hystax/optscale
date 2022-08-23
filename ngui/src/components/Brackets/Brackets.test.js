import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Brackets from "./Brackets";

it("renders without crashing (empty props)", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Brackets />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing (without children)", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Brackets type="round" bold />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing (with children)", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Brackets type="round" bold>
        {"brackets content"}
      </Brackets>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
