import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SideModalHeader from "./SideModalHeader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SideModalHeader messageId="deleteResources" onClose={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
