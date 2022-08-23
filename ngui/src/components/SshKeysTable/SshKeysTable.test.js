import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SshKeysTable from "./SshKeysTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SshKeysTable />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
