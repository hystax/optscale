import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { getBasicRelativeRangesSet } from "./defaults";
import RelativeDateTimePicker from "./RelativeDateTimePicker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RelativeDateTimePicker onChange={jest.fn} definedRanges={getBasicRelativeRangesSet()} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
