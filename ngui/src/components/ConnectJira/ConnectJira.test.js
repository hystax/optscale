import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ConnectJira from "./ConnectJira";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ConnectJira isLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
