import React from "react";
import ReactDOM from "react-dom";
import Button from "components/Button";
import TestProvider from "tests/TestProvider";
import IconError from "./IconError";

it("renders without crashing without children", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <IconError messageId="hystax" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with children", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <IconError messageId="hystax" />
      <Button variant="contained" color="primary" messageId="hystax" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
