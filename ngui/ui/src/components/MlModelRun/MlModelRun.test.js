import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlModelRun from "./MlModelRun";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlModelRun run={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
