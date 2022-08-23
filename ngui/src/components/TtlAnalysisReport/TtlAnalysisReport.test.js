import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TtlAnalysisReport from "./TtlAnalysisReport";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TtlAnalysisReport
        resourcesTracked={0}
        resourcesOutsideOfTtl={0}
        totalExpenses={0}
        expensesOutsideOfTtl={0}
        resources={[]}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
