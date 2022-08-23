import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DateRangePicker from "./DateRangePicker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DateRangePicker messageId="hystax" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
