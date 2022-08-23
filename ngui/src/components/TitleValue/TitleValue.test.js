import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TitleValue from "./TitleValue";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TitleValue />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
