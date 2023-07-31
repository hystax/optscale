import { START_TOUR, FINISH_TOUR, UPDATE_TOUR_STEP } from "./actionTypes";

export const startTour = (label, stepId) => ({
  label,
  type: START_TOUR,
  payload: stepId
});

export const updateTourStep = (label, stepId) => ({
  label,
  type: UPDATE_TOUR_STEP,
  payload: stepId
});

export const finishTour = (label) => ({
  label,
  type: FINISH_TOUR
});
