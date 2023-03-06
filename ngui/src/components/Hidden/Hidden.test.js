import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Hidden from "./Hidden";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Hidden mode="down" breakpoint="xl">
        test
      </Hidden>
    </TestProvider>
  );
  root.unmount();
});
