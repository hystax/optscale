import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import BufferedProgressBar from "./BufferedProgressBar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <BufferedProgressBar />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
