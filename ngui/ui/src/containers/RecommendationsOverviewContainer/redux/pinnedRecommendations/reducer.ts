import { PIN_RECOMMENDATION, UNPIN_RECOMMENDATION } from "./actionTypes";

export const PINNED_RECOMMENDATIONS = "pinnedRecommendations";

const reducer = (state = [], action) => {
  switch (action.type) {
    case PIN_RECOMMENDATION:
      if (!state.includes(action.payload)) {
        return [action.payload, ...state];
      }
      return state;
    case UNPIN_RECOMMENDATION:
      return state.filter((recommendationType) => recommendationType !== action.payload);
    default:
      return state;
  }
};

export default reducer;
