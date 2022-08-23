import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SummaryCardExtended from "./SummaryCardExtended";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <SummaryCardExtended
        value="$123456.321"
        caption="caption"
        relativeValue="relative value"
        relativeValueCaption="relative value caption"
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
