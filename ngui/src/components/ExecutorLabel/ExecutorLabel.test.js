import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ExecutorLabel from "./ExecutorLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExecutorLabel instanceId="instanceId" platformType="platformType" discovered={false} resource={null} />
    </TestProvider>
  );
  root.unmount();
});
