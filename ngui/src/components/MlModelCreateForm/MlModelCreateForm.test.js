import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlModelCreateForm from "./MlModelCreateForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlModelCreateForm onSubmit={jest.fn} onCancel={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
