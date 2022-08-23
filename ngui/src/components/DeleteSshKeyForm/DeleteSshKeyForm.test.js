import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DeleteSshKeyForm from "./DeleteSshKeyForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteSshKeyForm />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
