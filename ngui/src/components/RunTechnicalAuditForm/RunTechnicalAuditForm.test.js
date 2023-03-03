import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RunTechnicalAuditForm from "./RunTechnicalAuditForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RunTechnicalAuditForm onSubmit={jest.fn} />
    </TestProvider>
  );
  root.unmount();
});
