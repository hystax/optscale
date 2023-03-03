import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TrafficFromToLabel from "./TrafficFromToLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TrafficFromToLabel />
    </TestProvider>
  );
  root.unmount();
});
