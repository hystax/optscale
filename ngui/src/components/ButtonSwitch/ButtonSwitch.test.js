import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ButtonSwitch from "./ButtonSwitch";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ButtonSwitch buttons={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
