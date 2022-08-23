import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import FromToArrowLabel from "./FromToArrowLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <FromToArrowLabel from="from" to="to" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
