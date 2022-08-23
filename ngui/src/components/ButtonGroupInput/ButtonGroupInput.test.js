import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ButtonGroupInput from "./ButtonGroupInput";

it("renders with action", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ButtonGroupInput labelText="" helperText="" buttons={[]} activeButtonIndex={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
