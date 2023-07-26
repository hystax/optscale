import { UPDATE_COLLAPSED_MENU_ITEMS } from "./actionTypes";

export const COLLAPSED_MENU_ITEMS = "collapsedMenuItems";

const reducer = (state = [], action) => {
  switch (action.type) {
    case UPDATE_COLLAPSED_MENU_ITEMS:
      return action.payload;
    default:
      return state;
  }
};

export default reducer;
