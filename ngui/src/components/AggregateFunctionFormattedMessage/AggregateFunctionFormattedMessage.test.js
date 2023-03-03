import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AggregateFunctionFormattedMessage from "./AggregateFunctionFormattedMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AggregateFunctionFormattedMessage aggregateFunction="max" />
    </TestProvider>
  );
  root.unmount();
});
