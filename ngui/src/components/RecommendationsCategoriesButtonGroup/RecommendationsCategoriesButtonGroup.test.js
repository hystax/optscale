import React from "react";
import ReactDOM from "react-dom";
import { ALL_CATEGORY, SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";
import TestProvider from "tests/TestProvider";
import RecommendationsCategoriesButtonGroup from "./RecommendationsCategoriesButtonGroup";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationsCategoriesButtonGroup
        category={ALL_CATEGORY}
        onClick={jest.fn}
        categoriesSizes={Object.fromEntries(
          SUPPORTED_CATEGORIES.map((categoryName) => [categoryName, Math.floor(10 * Math.random())])
        )}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
