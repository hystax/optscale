import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PoolLabel from "./PoolLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PoolLabel name="name" type="type" />
    </TestProvider>
  );
  root.unmount();
});
