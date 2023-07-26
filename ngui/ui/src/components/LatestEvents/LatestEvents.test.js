import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LatestEvents from "./LatestEvents";

it("renders without crashing with 0 events", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LatestEvents count={0} />
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with 1 event", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LatestEvents count={1} />
    </TestProvider>
  );
  root.unmount();
});
