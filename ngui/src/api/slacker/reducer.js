import { SET_SLACK_INSTALLATION_PATH } from "./actionTypes";

export const SLACKER = "slacker";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SET_SLACK_INSTALLATION_PATH:
      return {
        ...state,
        [action.label]: action.payload
      };
    default:
      return state;
  }
};

export default reducer;
