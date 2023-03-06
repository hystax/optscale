import React from "react";
import RecommendationsCategoriesSelector from "components/RecommendationsCategoriesSelector";
import { ALL_CATEGORY, SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";

export default {
  title: "Components/RecommendationsCategoriesSelector",
  argTypes: {
    category: {
      name: "Category",
      control: "select",
      options: [SUPPORTED_CATEGORIES, ALL_CATEGORY],
      defaultValue: SUPPORTED_CATEGORIES[0]
    },
    categoriesSizes: {
      name: "Categories sizes",
      control: "object",
      defaultValue: Object.fromEntries(
        SUPPORTED_CATEGORIES.map((categoryName) => [categoryName, Math.floor(10 * Math.random())])
      )
    }
  }
};

export const basic = (args) => (
  <RecommendationsCategoriesSelector
    value={args.category}
    categoriesSizes={args.categoriesSizes}
    onChange={() => console.log("Click")}
  />
);
