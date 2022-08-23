import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Greeter from "./Greeter";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Greeter form={<div>Form</div>} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
