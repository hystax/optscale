import { SET_EXPANDED_ROWS } from "./actionTypes";

export const EXPANDED_POOL_ROWS = "expandedPoolRows";

const reducer = (state = [], action) => {
  switch (action.type) {
    case SET_EXPANDED_ROWS: {
      return action.payload;
    }
    default:
      return state;
  }
};

export default reducer;
