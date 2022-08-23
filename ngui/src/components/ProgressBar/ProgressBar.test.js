import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ProgressBar from "./ProgressBar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ProgressBar />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
