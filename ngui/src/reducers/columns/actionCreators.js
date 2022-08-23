import { SAVE_HIDDEN_COLUMNS } from "./actionTypes";

export const saveHiddenColumns = (tableUID, hiddenColumnsArray) => ({
  type: SAVE_HIDDEN_COLUMNS,
  payload: { hiddenColumnsArray, tableUID }
});
