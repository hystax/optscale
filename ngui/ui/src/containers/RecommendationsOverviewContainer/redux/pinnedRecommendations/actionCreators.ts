import { PIN_RECOMMENDATION, UNPIN_RECOMMENDATION } from "./actionTypes";

export const pinRecommendation = (recommendationType) => ({
  type: PIN_RECOMMENDATION,
  payload: recommendationType
});

export const unpinRecommendation = (recommendationType) => ({
  type: UNPIN_RECOMMENDATION,
  payload: recommendationType
});
