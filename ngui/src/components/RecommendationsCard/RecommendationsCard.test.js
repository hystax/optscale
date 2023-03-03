import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationsCard from "./RecommendationsCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationsCard possibleMonthlySavings={0} costRecommendationsCount={0} securityRecommendationsCount={0} />
    </TestProvider>
  );
  root.unmount();
});
