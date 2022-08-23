import { UPDATE_COLLAPSED_MENU_ITEMS } from "./actionTypes";

export const updateCollapsedMenuItems = (value) => ({
  type: UPDATE_COLLAPSED_MENU_ITEMS,
  payload: value
});
