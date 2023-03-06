import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MetricCard from "./MetricCard";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MetricCard title="title" cardBodyDefinition={{ emptyMessage: "message" }} />
    </TestProvider>
  );
  root.unmount();
});

it("renders chart without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MetricCard title="title" cardBodyDefinition={{ chartProps: { lines: [] } }} />
    </TestProvider>
  );
  root.unmount();
});
