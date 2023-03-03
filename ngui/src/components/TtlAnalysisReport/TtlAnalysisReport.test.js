import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TtlAnalysisReport from "./TtlAnalysisReport";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TtlAnalysisReport
        resourcesTracked={0}
        resourcesOutsideOfTtl={0}
        totalExpenses={0}
        expensesOutsideOfTtl={0}
        resources={[]}
      />
    </TestProvider>
  );
  root.unmount();
});
