import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import KeyValueLabelsList from "./KeyValueLabelsList";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <KeyValueLabelsList />
    </TestProvider>
  );
  root.unmount();
});
