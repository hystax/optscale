import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceUsageFormattedNumber from "./ResourceUsageFormattedNumber";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceUsageFormattedNumber usage={0} unit="GB" />
    </TestProvider>
  );
  root.unmount();
});
