import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SideModalTitle from "./SideModalTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SideModalTitle />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
