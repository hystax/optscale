import React from "react";
import RecommendationsCategoriesButtonGroup from "components/RecommendationsCategoriesButtonGroup";
import { select, object } from "@storybook/addon-knobs";
import { ALL_CATEGORY, SUPPORTED_CATEGORIES } from "components/RelevantRecommendations/constants";

export default {
  title: "Components/RecommendationsCategoriesButtonGroup"
};

export const basic = () => (
  <RecommendationsCategoriesButtonGroup
    category={select("category", SUPPORTED_CATEGORIES, ALL_CATEGORY)}
    categoriesSizes={object(
      "categoriesSizes",
      Object.fromEntries(SUPPORTED_CATEGORIES.map((categoryName) => [categoryName, Math.floor(10 * Math.random())]))
    )}
    onClick={() => console.log("Click")}
  />
);
