import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TagsBreakdown from "./TagsBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TagsBreakdown
        data={[]}
        appliedRange={{}}
        chartCountKeys={[]}
        chartCounts={{}}
        chartData={[]}
        updateSelectedTag={() => {}}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
