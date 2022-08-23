import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ActivityListener from "./ActivityListener";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ActivityListener>test</ActivityListener>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
