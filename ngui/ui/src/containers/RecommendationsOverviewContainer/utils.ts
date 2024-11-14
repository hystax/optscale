import { ALL_SERVICES } from "hooks/useRecommendationServices";
import { intl } from "translations/react-intl-config";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  CATEGORY_ALL,
  CATEGORY_COST,
  CATEGORY_SECURITY,
  CATEGORY_CRITICAL,
  CATEGORY_NON_EMPTY,
  RECOMMENDATION_COLOR
} from "./recommendations/BaseRecommendation";

export const categoryFilter = (category) => (recommendation) => {
  if (category === CATEGORY_ALL) {
    return true;
  }

  // two definitional categories
  if ([CATEGORY_COST, CATEGORY_SECURITY].includes(category)) {
    return recommendation.categories.includes(category);
  }

  if (category === CATEGORY_CRITICAL) {
    return recommendation.color === RECOMMENDATION_COLOR.ERROR;
  }

  if (category === CATEGORY_NON_EMPTY) {
    return recommendation.count !== 0;
  }

  return true;
};

export const serviceFilter = (service) => (recommendation) => {
  if (service === ALL_SERVICES) {
    return true;
  }

  return recommendation.services.includes(service);
};

export const searchFilter = (search) => (recommendation) => {
  if (!search) {
    return true;
  }

  const commonMessageValues = {
    strong: (chunks) => chunks,
    link: (chunks) => chunks
  };

  const description = intl
    .formatMessage(
      { id: recommendation.descriptionMessageId },
      { ...recommendation.descriptionMessageValues, ...commonMessageValues }
    )
    .toLocaleLowerCase();

  const title = intl.formatMessage({ id: recommendation.title }).toLocaleLowerCase();

  const searchLowerCase = search.toLocaleLowerCase();

  return title.includes(searchLowerCase) || description.includes(searchLowerCase);
};

export const appliedDataSourcesFilter = (selectedDataSourceTypes) => (recommendation) =>
  // Show all recommendaions if no data sources are selected
  isEmptyArray(selectedDataSourceTypes) ||
  !isEmptyArray(
    recommendation.appliedDataSources.filter((appliedDataSource) => selectedDataSourceTypes.includes(appliedDataSource))
  );
