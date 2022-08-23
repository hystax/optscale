import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import QuickDatePickerValues from "./QuickDatePickerValues";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <QuickDatePickerValues titleMessageId="setToNow" items={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
