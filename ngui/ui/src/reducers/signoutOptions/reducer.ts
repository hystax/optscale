import { SET_SIGNOUT_OPTIONS } from "./actionTypes";

export const SIGNOUT_OPTIONS = "signoutOptions";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_SIGNOUT_OPTIONS: {
      return action.payload;
    }
    default:
      return state;
  }
};

export default reducer;
