import React from "react";
import { createRoot } from "react-dom/client";
import RelativeDateTimePicker, { k8sRightsizingRelativeDates } from "components/RelativeDateTimePicker";
import TestProvider from "tests/TestProvider";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RelativeDateTimePicker onChange={jest.fn} definedRanges={k8sRightsizingRelativeDates} />
    </TestProvider>
  );
  root.unmount();
});
