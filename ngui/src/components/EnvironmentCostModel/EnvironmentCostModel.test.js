import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentCostModel from "./EnvironmentCostModel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentCostModel resourceId={""} hourlyPrice={0} />
    </TestProvider>
  );
  root.unmount();
});
