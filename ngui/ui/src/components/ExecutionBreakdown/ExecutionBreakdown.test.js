import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ExecutionBreakdown from "./ExecutionBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExecutionBreakdown breakdown={{}} milestones={[]} stages={[]} reachedGoals={[]} />
    </TestProvider>
  );
  root.unmount();
});
