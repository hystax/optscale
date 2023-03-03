import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AdvancedDataSourceDetails from "./AdvancedDataSourceDetails";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AdvancedDataSourceDetails
        lastImportAt={0}
        lastImportAttemptAt={0}
        lastImportAttemptError={""}
        lastMetricsRetrieval={0}
        lastMetricsRetrievalAttempt={0}
        lastGettingMetricAttemptError={0}
      />
    </TestProvider>
  );
  root.unmount();
});
