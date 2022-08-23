import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CloudResourceId from "./CloudResourceId";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudResourceId resourceId="" cloudResourceId="" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
