import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HeaderHelperCell from "./HeaderHelperCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HeaderHelperCell titleMessageId="name" helperMessageId="name" />
    </TestProvider>
  );
  root.unmount();
});
