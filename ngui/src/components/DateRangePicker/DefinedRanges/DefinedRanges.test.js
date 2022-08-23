import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DefinedRanges from "./DefinedRanges";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DefinedRanges ranges={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
