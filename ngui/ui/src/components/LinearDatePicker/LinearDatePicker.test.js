import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import LinearDatePicker from "./LinearDatePicker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LinearDatePicker selectedRange={{}} onSelectedRangeChange={jest.fn} ranges={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
