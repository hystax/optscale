import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Header from "./Header";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Header date={new Date()} userBounds={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
