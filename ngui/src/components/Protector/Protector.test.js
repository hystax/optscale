import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Protector from "./Protector";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Protector allowedActions={[]}>
        <div>test</div>
      </Protector>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
