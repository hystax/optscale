import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CheckboxLoader from "./CheckboxLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CheckboxLoader />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
