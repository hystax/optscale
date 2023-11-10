import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { getLength } from "utils/arrays";
import { pinRecommendation, unpinRecommendation } from "./actionCreators";
import { PINNED_RECOMMENDATIONS } from "./reducer";

export const usePinnedRecommendations = () => {
  const { rootData: pinnedRecommendations = [] } = useRootData(PINNED_RECOMMENDATIONS);

  return pinnedRecommendations;
};

export const useIsRecommendationPinned = (recommendationType) => {
  const pinnedRecommendations = usePinnedRecommendations();

  return pinnedRecommendations.includes(recommendationType);
};

export const usePinnedRecommendationsCount = () => {
  const pinnedRecommendations = usePinnedRecommendations();

  return getLength(pinnedRecommendations);
};

export const useRecommendationPinActions = (recommendationType) => {
  const dispatch = useDispatch();

  return {
    pin: () => dispatch(pinRecommendation(recommendationType)),
    unpin: () => dispatch(unpinRecommendation(recommendationType))
  };
};
