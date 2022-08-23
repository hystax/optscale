import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SummaryGrid from "./SummaryGrid";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SummaryGrid summaryData={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
