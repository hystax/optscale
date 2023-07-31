import { SET_DATE } from "./actionTypes";

export const RANGE_DATES = "rangeDates";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_DATE:
      return {
        ...state,
        [action.label]: {
          startDate: action.payload.startDate,
          endDate: action.payload.endDate
        }
      };
    default:
      return state;
  }
};

export default reducer;
