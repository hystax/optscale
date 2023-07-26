import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HeaderButtons from "./HeaderButtons";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HeaderButtons />
    </TestProvider>
  );
  root.unmount();
});
