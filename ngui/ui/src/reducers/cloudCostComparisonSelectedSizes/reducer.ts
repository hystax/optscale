import { ADD_SIZE, REMOVE_SIZE, RESET_SELECTION } from "./actionTypes";

export const CLOUD_COST_COMPARISON_SELECTED_SIZES = "cloudCostComparisonSelectedSizes";

const reducer = (state = [], action) => {
  switch (action.type) {
    case ADD_SIZE: {
      return [...state, action.payload];
    }
    case REMOVE_SIZE: {
      return state.filter((flavor) => flavor.id !== action.payload.id);
    }
    case RESET_SELECTION: {
      return [];
    }
    default:
      return state;
  }
};

export default reducer;
