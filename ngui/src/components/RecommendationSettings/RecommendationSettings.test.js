import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationSettings from "./RecommendationSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationSettings
        options={{}}
        backendRecommendationType="type"
        availablePools={[]}
        withExclusions
        withThresholds
        withRightsizingStrategy
      />
    </TestProvider>
  );
  root.unmount();
});
