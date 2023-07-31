import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationLimitWarning from "./RecommendationLimitWarning";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationLimitWarning limit={4} />
    </TestProvider>
  );
  root.unmount();
});
