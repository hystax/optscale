import { UPDATE_COLLAPSED_MENU_ITEMS } from "./actionTypes";

export const COLLAPSED_MENU_ITEMS = "collapsedMenuItems";

export const MAIN_MENU_SECTION_IDS = Object.freeze({
  HOME: "home",
  FINOPS: "finops",
  ML_OPS: "mlOps",
  POLICIES: "policies",
  SANDBOX: "sandbox",
  SYSTEM: "system"
});

const reducer = (state = [MAIN_MENU_SECTION_IDS.SANDBOX], action) => {
  switch (action.type) {
    case UPDATE_COLLAPSED_MENU_ITEMS:
      return action.payload;
    default:
      return state;
  }
};

export default reducer;
