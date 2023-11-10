import { UPDATE_MAIN_MENU_STATE } from "./actionTypes";

export const MAIN_MENU_EXPANDED = "mainMenuExpanded";

const reducer = (state = true, action) => {
  switch (action.type) {
    case UPDATE_MAIN_MENU_STATE:
      return action.payload;
    default:
      return state;
  }
};

export default reducer;
