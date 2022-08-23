import {
  ALL_CATEGORY,
  SECURITY_CATEGORY,
  SUPPORTED_CATEGORIES,
  COST_CATEGORY
} from "components/RelevantRecommendations/constants";
import {
  RECOMMENDATION_OBSOLETE_IPS,
  RECOMMENDATION_SHORT_LIVING_INSTANCES,
  RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
  RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  RECOMMENDATION_INSTANCE_MIGRATION,
  RECOMMENDATION_OBSOLETE_IMAGES,
  RECOMMENDATION_OBSOLETE_SNAPSHOTS,
  RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
  RECOMMENDATION_RESERVED_INSTANCES,
  RECOMMENDATION_INSTANCE_SUBSCRIPTION,
  RECOMMENDATION_RIGHTSIZING_INSTANCES,
  RECOMMENDATION_ABANDONED_INSTANCES,
  RECOMMENDATION_INSTANCES_FOR_SHUTDOWN,
  RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES,
  RECOMMENDATION_INACTIVE_USERS,
  RECOMMENDATION_INSECURE_SECURITY_GROUPS,
  RECOMMENDATION_INACTIVE_CONSOLE_USERS,
  RECOMMENDATION_ABANDONED_KINESIS_STREAMS,
  RECOMMENDATION_PUBLIC_S3_BUCKETS,
  RECOMMENDATION_ABANDONED_S3_BUCKETS,
  RECOMMENDATION_INSTANCES_GENERATION_UPGRADE
} from "./constants";

const ACTIVE = "active";
const DISMISSED = "dismissed";
const EXCLUDED = "excluded";

const getRecommendationCategoryByName = (recommendationName) =>
  ({
    [RECOMMENDATION_SHORT_LIVING_INSTANCES]: COST_CATEGORY,
    [RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME]: COST_CATEGORY,
    [RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME]: COST_CATEGORY,
    [RECOMMENDATION_INSTANCE_MIGRATION]: COST_CATEGORY,
    [RECOMMENDATION_OBSOLETE_IMAGES]: COST_CATEGORY,
    [RECOMMENDATION_OBSOLETE_SNAPSHOTS]: COST_CATEGORY,
    [RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS]: COST_CATEGORY,
    [RECOMMENDATION_RESERVED_INSTANCES]: COST_CATEGORY,
    [RECOMMENDATION_INSTANCE_SUBSCRIPTION]: COST_CATEGORY,
    [RECOMMENDATION_RIGHTSIZING_INSTANCES]: COST_CATEGORY,
    [RECOMMENDATION_ABANDONED_INSTANCES]: COST_CATEGORY,
    [RECOMMENDATION_INSTANCES_FOR_SHUTDOWN]: COST_CATEGORY,
    [RECOMMENDATION_RIGHTSIZING_RDS_INSTANCES]: COST_CATEGORY,
    [RECOMMENDATION_INACTIVE_USERS]: SECURITY_CATEGORY,
    [RECOMMENDATION_INACTIVE_CONSOLE_USERS]: SECURITY_CATEGORY,
    [RECOMMENDATION_INSECURE_SECURITY_GROUPS]: SECURITY_CATEGORY,
    [RECOMMENDATION_INSTANCES_GENERATION_UPGRADE]: COST_CATEGORY,
    [RECOMMENDATION_OBSOLETE_IPS]: COST_CATEGORY,
    [RECOMMENDATION_ABANDONED_KINESIS_STREAMS]: COST_CATEGORY,
    [RECOMMENDATION_PUBLIC_S3_BUCKETS]: SECURITY_CATEGORY,
    [RECOMMENDATION_ABANDONED_S3_BUCKETS]: COST_CATEGORY
  }[recommendationName]);

const getCategorizesSizes = (categorizedRecommendations) =>
  Object.fromEntries(Object.entries(categorizedRecommendations).map(([category, { count }]) => [category, count]));

export const categorizeRecommendations = (
  activeOptimizations = {},
  dismissedOptimizations = {},
  excludedOptimizations = {}
) => {
  const categorizedRecommendations = Object.fromEntries(
    SUPPORTED_CATEGORIES.map((categoryName) => [categoryName, { [ACTIVE]: {}, [DISMISSED]: {}, [EXCLUDED]: {}, count: 0 }])
  );

  const addRecommendationInfoToCategorizedRecommendations = (recommendationInfo, path) => {
    const [category, type, recommendationName] = path;
    categorizedRecommendations[category][type][recommendationName] = recommendationInfo;
  };

  const incrementCategorizedRecommendationsCount = (categoryName, count) => {
    categorizedRecommendations[categoryName].count += count;
  };

  const groupRecommendations = (type, recommendations) =>
    Object.entries(recommendations).forEach(([recommendationName, recommendationInfo]) => {
      addRecommendationInfoToCategorizedRecommendations(recommendationInfo, [ALL_CATEGORY, type, recommendationName]);
      incrementCategorizedRecommendationsCount(ALL_CATEGORY, recommendationInfo.count);

      const category = getRecommendationCategoryByName(recommendationName);

      if (category) {
        addRecommendationInfoToCategorizedRecommendations(recommendationInfo, [category, type, recommendationName]);
        incrementCategorizedRecommendationsCount(category, recommendationInfo.count);
      }
    });

  groupRecommendations(ACTIVE, activeOptimizations);
  groupRecommendations(DISMISSED, dismissedOptimizations);
  groupRecommendations(EXCLUDED, excludedOptimizations);

  return {
    categorizedRecommendations,
    categoriesSizes: getCategorizesSizes(categorizedRecommendations)
  };
};

export const getActiveRecommendationsByCategory = (recommendations, categoryName) =>
  recommendations[categoryName]?.[ACTIVE] ?? {};

export const getDismissedRecommendationsByCategory = (recommendations, categoryName) =>
  recommendations[categoryName]?.[DISMISSED] ?? {};

export const getExcludedRecommendationsByCategory = (recommendations, categoryName) =>
  recommendations[categoryName]?.[EXCLUDED] ?? {};

export const mockCategorizedRecommendations = (rawRecommendations) => {
  const { categorizedRecommendations, categoriesSizes } = categorizeRecommendations(
    rawRecommendations.optimizations,
    rawRecommendations.dismissed_optimizations,
    rawRecommendations.excluded_optimizations
  );

  return {
    ...rawRecommendations,
    categorizedRecommendations,
    categoriesSizes
  };
};
