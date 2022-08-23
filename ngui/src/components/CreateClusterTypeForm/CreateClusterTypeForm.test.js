import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CreateClusterTypeForm from "./CreateClusterTypeForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CreateClusterTypeForm onSubmit={jest.fn} onCancel={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
