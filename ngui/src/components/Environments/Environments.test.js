import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Environments from "./Environments";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Environments environments={[]} onUpdateActivity={() => {}} entityId="123" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
