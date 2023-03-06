import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SummaryCardExtended from "./SummaryCardExtended";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SummaryCardExtended
        value="$123456.321"
        caption="caption"
        relativeValue="relative value"
        relativeValueCaption="relative value caption"
      />
    </TestProvider>
  );
  root.unmount();
});
