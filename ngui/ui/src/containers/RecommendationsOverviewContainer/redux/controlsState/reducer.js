import { SET_CATEGORY, SET_SERVICE, SET_VIEW } from "./actionTypes";

export const RECOMMENDATIONS_CONTROLS_STATE = "recommendationsControlState";

export const VALUE_ACCESSORS = Object.freeze({
  CATEGORY: "category",
  SERVICE: "service",
  VIEW: "view"
});

const reducer = (state = [], action) => {
  switch (action.type) {
    case SET_CATEGORY:
      return {
        ...state,
        [VALUE_ACCESSORS.CATEGORY]: action.payload
      };
    case SET_SERVICE:
      return {
        ...state,
        [VALUE_ACCESSORS.SERVICE]: action.payload
      };
    case SET_VIEW:
      return {
        ...state,
        [VALUE_ACCESSORS.VIEW]: action.payload
      };
    default:
      return state;
  }
};

export default reducer;
