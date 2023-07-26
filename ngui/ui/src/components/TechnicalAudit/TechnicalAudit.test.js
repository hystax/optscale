import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TechnicalAudit from "./TechnicalAudit";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TechnicalAudit />
    </TestProvider>
  );
  root.unmount();
});
