import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MetricChart from "./MetricChart";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MetricChart lines={[]} />
    </TestProvider>
  );
  root.unmount();
});
