import { SET_APPLICATION_BREAKDOWNS } from "./actionTypes";

export const APPLICATION_BREAKDOWN = "applicationBreakdown";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_APPLICATION_BREAKDOWNS:
      return {
        ...state,
        [action.payload.id]: {
          ...state[action.payload.id],
          [action.payload.storeId]: action.payload.breakdowns
        }
      };
    default:
      return state;
  }
};

export default reducer;
