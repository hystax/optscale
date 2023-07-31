import React from "react";
import { createRoot } from "react-dom/client";
import { k8sRightsizingRelativeDates } from "components/RelativeDateTimePicker";
import TestProvider from "tests/TestProvider";
import K8sRightsizing from "./K8sRightsizing";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <K8sRightsizing
        applyFilter={jest.fn}
        actionBarDefinition={{}}
        definedRanges={k8sRightsizingRelativeDates}
        namespaces={[]}
      />
    </TestProvider>
  );
  root.unmount();
});
