import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SummaryCard from "./SummaryCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SummaryCard value="$123456.321" caption="This is some caption" help={{ show: true, messageId: "hystax" }} />
    </TestProvider>
  );
  root.unmount();
});
