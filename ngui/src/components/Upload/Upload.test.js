import React from "react";
import ReactDOM from "react-dom";
import "regenerator-runtime/runtime";
import TestProvider from "tests/TestProvider";
import Upload from "./Upload";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Upload acceptedFiles={[]} handleChange={jest.fn} setErrorText={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
