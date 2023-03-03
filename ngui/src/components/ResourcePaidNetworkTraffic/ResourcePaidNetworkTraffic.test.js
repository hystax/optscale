import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourcePaidNetworkTraffic from "./ResourcePaidNetworkTraffic";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourcePaidNetworkTraffic trafficExpenses={[]} />
    </TestProvider>
  );
  root.unmount();
});
