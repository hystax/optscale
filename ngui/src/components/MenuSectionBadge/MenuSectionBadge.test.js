import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MenuSectionBadge from "./MenuSectionBadge";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MenuSectionBadge messageId="name" />
    </TestProvider>
  );
  root.unmount();
});
