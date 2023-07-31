import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import InfoRow from "./InfoRow";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <InfoRow title={"test title"} value={"test value"} />
    </TestProvider>
  );
  root.unmount();
});
