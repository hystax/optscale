import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ConnectForm from "./ConnectForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ConnectForm>{() => null}</ConnectForm>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
