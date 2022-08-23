import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DetectedConstraintsHistoryTable from "./DetectedConstraintsHistoryTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DetectedConstraintsHistoryTable limitHits={[]} constraint={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
