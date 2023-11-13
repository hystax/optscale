import { SET_DATE } from "./actionTypes";

export const setDate = (startDate, endDate, label) => ({
  type: SET_DATE,
  payload: {
    startDate,
    endDate
  },
  label
});
