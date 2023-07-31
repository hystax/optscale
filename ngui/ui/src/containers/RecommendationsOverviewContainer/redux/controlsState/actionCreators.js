import { SET_CATEGORY, SET_SERVICE, SET_VIEW } from "./actionTypes";

export const setCategory = (category) => ({
  type: SET_CATEGORY,
  payload: category
});

export const setService = (service) => ({
  type: SET_SERVICE,
  payload: service
});

export const setView = (view) => ({
  type: SET_VIEW,
  payload: view
});
