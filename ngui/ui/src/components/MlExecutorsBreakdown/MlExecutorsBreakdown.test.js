import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import MlExecutorsBreakdown from "./MlExecutorsBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlExecutorsBreakdown breakdown={[]} breakdownBy={ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU} />
    </TestProvider>
  );
  root.unmount();
});
