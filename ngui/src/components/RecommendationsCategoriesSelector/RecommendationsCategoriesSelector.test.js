import React from "react";
import { createRoot } from "react-dom/client";
import { SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";
import TestProvider from "tests/TestProvider";
import RecommendationsCategoriesSelector from "./RecommendationsCategoriesSelector";

it("renders without crashing", () => {
  const sizes = Object.fromEntries(SUPPORTED_CATEGORIES.map((categoryName) => [categoryName, Math.floor(10 * Math.random())]));
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationsCategoriesSelector value={SUPPORTED_CATEGORIES[0]} onChange={jest.fn} categoriesSizes={sizes} />
    </TestProvider>
  );
  root.unmount();
});
