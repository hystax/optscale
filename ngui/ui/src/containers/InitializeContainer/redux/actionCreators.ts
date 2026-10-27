import { INITIALIZE } from "./actionTypes";

export const initialize = (value) => ({
  type: INITIALIZE,
  payload: value,
});
