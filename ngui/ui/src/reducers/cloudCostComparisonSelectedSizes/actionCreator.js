import { ADD_SIZE, REMOVE_SIZE, RESET_SELECTION } from "./actionTypes";

export const addSize = (size) => ({
  type: ADD_SIZE,
  payload: size
});

export const removeSizes = (size) => ({
  type: REMOVE_SIZE,
  payload: size
});

export const resetSelection = () => ({
  type: RESET_SELECTION
});
