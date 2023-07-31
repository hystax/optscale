import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PoolTypeSelector from "./PoolTypeSelector";

it("renders with action", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolTypeSelector />
    </TestProvider>
  );
  root.unmount();
});
