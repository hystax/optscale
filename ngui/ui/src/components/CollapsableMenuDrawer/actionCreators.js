import { UPDATE_MAIN_MENU_STATE } from "./actionTypes";

export const updateMainMenuState = (value) => ({
  type: UPDATE_MAIN_MENU_STATE,
  payload: value
});
