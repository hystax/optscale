import { SET_MODEL_OVERVIEW_CHART } from "./actionTypes";

export const MODEL_BREAKDOWN = "modelBreakdown";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_MODEL_OVERVIEW_CHART: {
      return {
        ...state,
        [action.payload.id]: {
          ...state[action.payload.id],
          [action.payload.storeId]: action.payload.breakdowns
        }
      };
    }
    default:
      return state;
  }
};

export default reducer;
