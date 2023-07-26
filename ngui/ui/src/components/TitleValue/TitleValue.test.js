import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TitleValue from "./TitleValue";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TitleValue />
    </TestProvider>
  );
  root.unmount();
});
