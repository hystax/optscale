import { SET_EXPANDED_ROW, SET_EXPANDED_ROWS } from "./actionTypes";

export const setExpandedRow = (poolId, isExpanded) => ({
  type: SET_EXPANDED_ROW,
  payload: { poolId, isExpanded }
});

export const setExpandedRows = (data) => ({
  type: SET_EXPANDED_ROWS,
  payload: data
});
