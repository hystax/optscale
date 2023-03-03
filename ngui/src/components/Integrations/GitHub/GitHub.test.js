import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import GitHub from "./GitHub";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <GitHub />
    </TestProvider>
  );
  root.unmount();
});
