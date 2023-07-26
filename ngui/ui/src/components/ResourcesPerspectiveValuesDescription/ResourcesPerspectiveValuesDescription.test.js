import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourcesPerspectiveValuesDescription from "./ResourcesPerspectiveValuesDescription";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourcesPerspectiveValuesDescription breakdownBy="expenses" />
    </TestProvider>
  );
  root.unmount();
});
