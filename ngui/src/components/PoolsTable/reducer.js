import { SET_EXPANDED_ROW, SET_EXPANDED_ROWS } from "./actionTypes";

export const EXPANDED_POOL_ROWS = "expandedPoolRows";

const setExpendedRows = (state, poolId, isExpanded) => {
  if (state.includes(poolId) && !isExpanded) {
    return state.filter((item) => item !== poolId);
  }
  return [...state, poolId];
};

const reducer = (state = [], action) => {
  switch (action.type) {
    case SET_EXPANDED_ROW: {
      return setExpendedRows(state, action.payload.poolId, action.payload.isExpanded);
    }
    case SET_EXPANDED_ROWS: {
      const result = action.payload.reduce((resultArray, id) => {
        if (state.includes(id)) {
          return resultArray;
        }
        return [...resultArray, id];
      }, []);
      return [...state, ...result];
    }
    default:
      return state;
  }
};

export default reducer;
