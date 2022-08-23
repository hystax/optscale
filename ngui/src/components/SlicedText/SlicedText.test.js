import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SlicedText from "./SlicedText";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SlicedText limit={1} text="test" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
