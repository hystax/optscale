import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Hidden from "./Hidden";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Hidden mode="down" breakpoint="xl">
        test
      </Hidden>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
