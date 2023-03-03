import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ContentBackdrop from "./ContentBackdrop";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ContentBackdrop messageType="cloudAccounts" />
    </TestProvider>
  );
  root.unmount();
});
