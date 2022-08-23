import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnabledConstraints from "./EnabledConstraints";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnabledConstraints render={(type) => type} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
