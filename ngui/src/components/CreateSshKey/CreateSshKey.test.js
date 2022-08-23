import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CreateSshKey from "./CreateSshKey";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CreateSshKey />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
