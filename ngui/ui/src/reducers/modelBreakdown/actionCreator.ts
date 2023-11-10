import { SET_MODEL_BREAKDOWNS } from "./actionTypes";

export const setBreakdowns = (storeId, modelId, breakdowns) => ({
  type: SET_MODEL_BREAKDOWNS,
  payload: { storeId, id: modelId, breakdowns }
});
