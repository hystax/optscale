import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SummaryCard from "./SummaryCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SummaryCard value="$123456.321" caption="This is some caption" help={{ show: true, messageId: "hystax" }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
