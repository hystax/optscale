import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ChipFiltersWrapper from "./ChipFiltersWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ChipFiltersWrapper chips={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
